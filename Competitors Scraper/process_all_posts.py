import os
import json
import time
import sys
import re
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
TRANSLATION_WORKERS = 10   # parallel translation threads (tune to your network)
CHUNK_SIZE          = 4500  # max chars per Google Translate call


# ──────────────────────────────────────────────
# TRANSLATION
# ──────────────────────────────────────────────
def _has_non_ascii(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)


def translate_with_retry(text: str, retries: int = 3, delay: float = 1.0) -> str:
    """Translate text to English, with retry and Arabic fallback."""
    if not text:
        return ''

    for attempt in range(retries):
        try:
            if len(text) > CHUNK_SIZE:
                parts = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
                translated = ' '.join(
                    GoogleTranslator(source='auto', target='en').translate(p) for p in parts
                )
            else:
                translated = GoogleTranslator(source='auto', target='en').translate(text)

            # If auto-detect returned the original unchanged, try forcing Arabic
            if translated.strip() == text.strip() and _has_non_ascii(text):
                print(f"translate_with_retry: auto returned original; trying forced ar→en", file=sys.stderr)
                try:
                    ar = GoogleTranslator(source='ar', target='en').translate(text)
                    if ar and ar.strip() != text.strip():
                        return ar
                except Exception as exc:
                    print(f"translate_with_retry: ar fallback failed: {exc}", file=sys.stderr)

            return translated

        except Exception as e:
            print(f"translate_with_retry: attempt {attempt + 1} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print("translate_with_retry: returning original after all retries", file=sys.stderr)
                return text

    return text


# ──────────────────────────────────────────────
# TEXT CLEANING
# ──────────────────────────────────────────────
def remove_urls(text: str) -> str:
    return re.sub(r'https?://\S+|www\.\S+', '', text) if text else text


def remove_emojis(text: str) -> str:
    if not text:
        return text
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\u2600-\u26FF"
        u"\u2700-\u27BF"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub('', text)


def clean_text(text: str) -> str:
    if not text:
        return ''
    t = remove_urls(text)
    t = remove_emojis(t)
    t = re.sub(r'[\uFE0F\u200B]', '', t)   # zero-width / variation selectors
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# ──────────────────────────────────────────────
# FIELD EXTRACTORS
# ──────────────────────────────────────────────
def get_reaction_count(post: dict) -> int:
    for k in ('reaction_count.count', 'reaction_count', 'likes'):
        if k in post:
            try:
                return int(post.get(k) or 0)
            except Exception:
                pass
    eng = post.get('engagement_stats') or {}
    if isinstance(eng, dict) and eng.get('likes') is not None:
        try:
            return int(eng.get('likes') or 0)
        except Exception:
            pass
    sub = post.get('sub_reactions') or {}
    if isinstance(sub, dict):
        try:
            return sum(int(v or 0) for v in sub.values())
        except Exception:
            pass
    return 0


def get_context_text(post: dict) -> str:
    for k in ('context', 'message', 'text'):
        if k in post:
            v = post.get(k)
            return '' if v is None else str(v)
    return ''


# ──────────────────────────────────────────────
# PER-POST WORKER  (runs in thread pool)
# ──────────────────────────────────────────────
def _process_post(post: dict):
    """
    Translate + clean a single post.
    Returns a normalized dict, or None if the post should be skipped.
    """
    rc  = get_reaction_count(post)
    ctx = get_context_text(post).strip()

    if not ctx:
        return None

    translated = translate_with_retry(ctx)
    if not translated or not translated.strip():
        return None

    cleaned = clean_text(translated)
    if not cleaned:
        return None

    return {'context': cleaned, 'reaction_count': rc}


# ──────────────────────────────────────────────
# MAIN PROCESSING
# ──────────────────────────────────────────────
def process_file(input_path: str, output_path: str):
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)

    # ── Collect raw posts ──
    posts = []
    if isinstance(data, dict) and 'results' in data and isinstance(data['results'], dict):
        for lst in data['results'].values():
            if isinstance(lst, list):
                posts.extend(lst)
    elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
        posts = data['data']
    elif isinstance(data, list):
        posts = data
    else:
        raise ValueError('Unrecognized input JSON structure')

    total = len(posts)
    print(f"Processing {total} posts with {TRANSLATION_WORKERS} parallel translation workers…")

    # ── Parallel translate + clean ──
    normalized = []
    done = 0

    with ThreadPoolExecutor(max_workers=TRANSLATION_WORKERS) as pool:
        future_map = {pool.submit(_process_post, post): post for post in posts}
        for future in as_completed(future_map):
            done += 1
            if done % 20 == 0 or done == total:
                print(f"  [{done}/{total}] translated…")
            try:
                result = future.result()
                if result is not None:
                    normalized.append(result)
            except Exception as e:
                print(f"  ⚠️ Post failed: {e}", file=sys.stderr)

    # ── Sort by reaction count ──
    normalized.sort(key=lambda x: x['reaction_count'], reverse=True)

    out = {
        'metadata': {
            'source_file':      str(p),
            'total_raw':        total,
            'total_extracted':  len(normalized),
        },
        'data': normalized,
    }

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with out_p.open('w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Wrote {len(normalized)} posts → {out_p}")
    return out_p


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == '__main__':
    RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = Path(RESULTS_DIR) / 'final_posts.json'

    if len(sys.argv) > 1 and sys.argv[1].strip():
        inp = sys.argv[1]
    else:
        candidates = glob.glob(os.path.join(RESULTS_DIR, "all_posts_*.json"))
        if candidates:
            candidates.sort(key=lambda p: Path(p).stat().st_mtime, reverse=True)
            inp = candidates[0]
        else:
            raise FileNotFoundError(
                    f"No input file found. Run the pipeline first so results appear in: {RESULTS_DIR}"
                )

    print(f"Processing input: {inp}")
    process_file(inp, str(out))
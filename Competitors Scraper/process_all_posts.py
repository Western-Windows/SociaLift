import json
import time
from pathlib import Path
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='en')


def translate_with_retry(text, retries=3, delay=1):
    for attempt in range(retries):
        try:
            if not text:
                return ''
            if len(text) > 4500:
                parts = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_parts = [translator.translate(part) for part in parts]
                return ' '.join(translated_parts)
            return translator.translate(text)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return text
    return text


def get_reaction_count(post: dict) -> int:
    # Common keys
    for k in ('reaction_count.count', 'reaction_count', 'likes'):
        if k in post:
            try:
                return int(post.get(k) or 0)
            except Exception:
                pass
    # Try engagement_stats.likes
    eng = post.get('engagement_stats') or {}
    if isinstance(eng, dict) and eng.get('likes') is not None:
        try:
            return int(eng.get('likes') or 0)
        except Exception:
            pass
    # Try sub_reactions sum
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
            if v is None:
                return ''
            return str(v)
    return ''


def process_file(input_path: str, output_path: str):
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)

    # Flatten posts: support top-level 'results' mapping as in your file
    posts = []
    if isinstance(data, dict) and 'results' in data and isinstance(data['results'], dict):
        for key, lst in data['results'].items():
            if isinstance(lst, list):
                for item in lst:
                    posts.append(item)
    elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
        posts = data['data']
    elif isinstance(data, list):
        posts = data
    else:
        raise ValueError('Unrecognized input JSON structure')

    normalized = []
    for post in posts:
        rc = get_reaction_count(post)
        ctx = get_context_text(post).strip()
        # If has reaction (>0) but no context, skip
        if rc > 0 and not ctx:
            continue
        # translate
        translated = translate_with_retry(ctx)
        normalized.append({
            'post_id': post.get('post_id') or post.get('id'),
            'published_date': post.get('published_date') or post.get('clean_date'),
            'reaction_count': rc,
            'context': translated,
            'raw': post
        })
        time.sleep(0.1)

    # Sort by reaction_count desc
    normalized.sort(key=lambda x: x['reaction_count'], reverse=True)

    out = {
        'metadata': {
            'source_file': str(p),
            'total_extracted': len(normalized),
        },
        'data': normalized
    }

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with out_p.open('w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(normalized)} posts to {out_p}")
    return out_p


if __name__ == '__main__':
    # Default input as provided
    inp = r"D:\Graduation Project\SociaLift\all_posts_20260217_191742.json"
    out = Path(__file__).resolve().parent / 'final_posts.json'
    process_file(inp, str(out))

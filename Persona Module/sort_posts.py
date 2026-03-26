import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import GoogleTranslator

def translate_with_retry(text, retries=3, delay=2):
    if not text:
        return ""
    
    translator = GoogleTranslator(source='auto', target='en')
    for attempt in range(retries):
        try:
            if len(text) > 4500:
                parts = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_parts = [translator.translate(part) for part in parts]
                return ' '.join(translated_parts)
            return translator.translate(text)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"  Translation failed after {retries} attempts: {e}")
                return text
    return text

def get_reaction_count(p):
    if isinstance(p, dict):
        eng = p.get('engagement_stats') or {}
        if isinstance(eng, dict) and eng.get('likes') is not None:
            try:
                return int(eng.get('likes') or 0)
            except Exception:
                pass
        for k in ('reaction_count.count', 'reaction_count', 'likes', 'engagement_count'):
            if k in p:
                try:
                    return int(p.get(k) or 0)
                except Exception:
                    pass
    return 0

def process_and_sort_posts(input_path: str | Path, output_path: str | Path, max_workers: int = 5):
    """Sorts posts by engagement and translates their content concurrently."""
    print('\n2) Translating & sorting posts (concurrently)...')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    posts = data.get('data', data) if isinstance(data, dict) else data
    sorted_posts = sorted(posts, key=get_reaction_count, reverse=True)

    def process_post(post):
        context = post.get('message') or post.get('context') or ''
        translated = translate_with_retry(context)
        return {
            "reaction_count": get_reaction_count(post),
            "context": translated
        }

    # Use ThreadPoolExecutor for concurrent translation
    unordered_results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks and keep track of their original index to maintain sorted order
        futures = {executor.submit(process_post, post): i for i, post in enumerate(sorted_posts)}
        
        for future in as_completed(futures):
            index = futures[future]
            try:
                unordered_results[index] = future.result()
            except Exception as e:
                print(f"Post processing failed: {e}")
                unordered_results[index] = {"reaction_count": get_reaction_count(sorted_posts[index]), "context": ""}
                
    # Reconstruct the sorted list using the original indices
    result = [unordered_results[i] for i in range(len(sorted_posts))]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"   Saved to {output_path}")
    return output_path
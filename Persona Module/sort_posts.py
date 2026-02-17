import json
import time
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='en')

def translate_with_retry(text, retries=3, delay=2):
    for attempt in range(retries):
        try:
            if len(text) > 4500:
                parts = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_parts = [translator.translate(part) for part in parts]
                return ' '.join(translated_parts)
            result = translator.translate(text)
            return result
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt + 1}/{retries} after error: {e}")
                time.sleep(delay)
            else:
                print(f"  Translation failed after {retries} attempts: {e}")
                return text
    return text

with open('d:/SociaLift/fb_full_history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Support both list-of-posts or {'data': [...]}
posts = data['data'] if isinstance(data, dict) and 'data' in data else data

def get_reaction_count(p):
    # prefer engagement_stats.likes from exporter
    if isinstance(p, dict):
        eng = p.get('engagement_stats') or {}
        if isinstance(eng, dict) and eng.get('likes') is not None:
            try:
                return int(eng.get('likes') or 0)
            except Exception:
                pass
        # fallback to common legacy keys
        for k in ('reaction_count.count', 'reaction_count', 'likes', 'engagement_count'):
            if k in p:
                try:
                    return int(p.get(k) or 0)
                except Exception:
                    pass
    return 0

sorted_posts = sorted(posts, key=get_reaction_count, reverse=True)

# Extract message (or context), translate, and save normalized sorted list
result = []
for i, post in enumerate(sorted_posts):
    context = ''
    if isinstance(post, dict):
        context = post.get('message') or post.get('context') or ''
    print(f"Translating post {i+1}/{len(sorted_posts)} ({get_reaction_count(post)} reactions)...")
    translated = translate_with_retry(context or '')

    result.append({
        "reaction_count": get_reaction_count(post),
        "context": translated
    })
    time.sleep(0.5)

# Save to JSON file
out_path = 'd:/SociaLift/sorted_posts.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {out_path}")

for item in result:
    print(f"Reactions: {item['reaction_count']}")
    print(f"Context: {item['context']}")
    print('-' * 80)

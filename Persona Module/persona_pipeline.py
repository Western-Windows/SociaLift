import os
import sys
import json
from pathlib import Path

# Standard Imports from local modules
from sort_posts import process_and_sort_posts
from preprocessing import preprocess_context
from personatone import generate_persona_options, load_top_posts

# Paths
WORKSPACE = Path(__file__).resolve().parents[1]
GRAPH_DIR = WORKSPACE / 'Graph API'
FB_FULL_PATH = WORKSPACE / 'fb_full_history.json'
SORTED_PATH = WORKSPACE / 'sorted_posts.json'
CLEANED_PATH = WORKSPACE / 'sorted_posts_cleaned.json'
FINAL_PERSONA_PATH = WORKSPACE / 'Persona Module' / 'final_persona.json'

def run_graph_api_export():
    print('\n1) Running Graph API exporter to fetch posts...')
    # Dynamically handle Graph API import from the sibling directory
    if str(GRAPH_DIR) not in sys.path:
        sys.path.insert(0, str(GRAPH_DIR))
    
    try:
        from get_posts_insights import FacebookAnalyticsManager
        manager = FacebookAnalyticsManager()
        raw_posts = manager.get_posts(limit=None)
        processed = manager.process_data(raw_posts)
        manager.export_to_json(processed, filename=str(FB_FULL_PATH))
        print(f'   Saved exporter output to: {FB_FULL_PATH}')
        return FB_FULL_PATH
    except ImportError as e:
        print(f"⚠️ Could not import Graph API module: {e}")
        print(f"   Assuming {FB_FULL_PATH} already exists and proceeding.")
        return FB_FULL_PATH

def main():
    print("="*60)
    print("  🎭 SOCIALIFT PERSONA PIPELINE")
    print("="*60)
    
    target_audience = input("\n👥 Describe your Target Audience (e.g., 'Young professionals aged 25-35'):\n   > ").strip()
    if not target_audience:
        print("\n⚠️ No audience provided. Using generic fallback.")
        target_audience = "General audience interested in our brand."

    try:
        # 1. Fetch
        run_graph_api_export()
        
        # 2. Sort & Translate
        process_and_sort_posts(FB_FULL_PATH, SORTED_PATH)
        
        # 3. Preprocess
        print('\n3) Running preprocessing on sorted posts...')
        preprocess_context(str(SORTED_PATH), str(CLEANED_PATH))
        
        # 4. Generate Persona
        print('\n4) Running persona analysis...')
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            api_key = input('🔑 OpenAI key not found in env. Please enter it: ').strip()

        top_posts_text = load_top_posts(str(CLEANED_PATH), top_n=10)
        
        if not top_posts_text.strip():
            print("\n⚠️ No historical posts found in the scraped data.")
            print("Please provide a 'template post' (an example of how you want your brand to sound).")
            input_text = input("   > ").strip()
            print(f"\n   Generating 3 Persona options from template post...")
        else:
            input_text = top_posts_text
            print(f"\n   Generating 3 Persona options from top performing posts...")

        persona_options = generate_persona_options(target_audience, input_text, api_key=api_key)
        
        print("\n" + "="*60)
        print("  🎯 SELECT YOUR PREFERRED BRAND PERSONA")
        print("="*60)
        
        for i, option in enumerate(persona_options.options, 1):
            print(f"\n[{i}] 🎭 ARCHETYPE: {option.archetype}")
            print(f"    🗣️ TONE: {option.emotional_tone}")
            print(f"    🔑 KEYWORDS: {', '.join(option.keywords)}")
            print(f"    📝 VOICE: {option.voice_description}")
            print("-" * 60)
            
        while True:
            try:
                choice = int(input("\n👉 Enter the number of your preferred persona (1, 2, or 3): ").strip())
                if choice in [1, 2, 3]:
                    selected_persona = persona_options.options[choice-1]
                    break
                else:
                    print("❌ Please enter exactly 1, 2, or 3.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                
        # Ensure target folder exists
        FINAL_PERSONA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(FINAL_PERSONA_PATH, 'w', encoding='utf-8') as f:
            json.dump(selected_persona.model_dump(), f, ensure_ascii=False, indent=2)
            
        print('\n' + '='*60)
        print('🎉 Persona Pipeline Complete!')
        print(f'📂 Final file: {FINAL_PERSONA_PATH}')
        print('='*60)
        
    except Exception as e:
        print('\n❌ Pipeline failed:', e)

if __name__ == '__main__':
    main()
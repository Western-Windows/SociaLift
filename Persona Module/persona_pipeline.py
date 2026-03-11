import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

# Pipeline: Graph API -> sort_posts.py -> preprocessing -> personatone
# Paths
WORKSPACE = Path(__file__).resolve().parents[1]
GRAPH_SCRIPT = WORKSPACE / 'Graph API' / 'get_posts_insights.py'
SORT_SCRIPT = WORKSPACE / 'Persona Module' / 'sort_posts.py'
PREPROCESS_MODULE = WORKSPACE / 'Persona Module' / 'preprocessing.py'
PERSONA_MODULE = WORKSPACE / 'Persona Module' / 'personatone.py'

FB_FULL_PATH = WORKSPACE / 'fb_full_history.json'
SORTED_PATH = WORKSPACE / 'sorted_posts.json'
CLEANED_PATH = WORKSPACE / 'sorted_posts_cleaned.json'
FINAL_PERSONA_PATH = WORKSPACE / 'Persona Module' / 'final_persona.json'

def load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot create module spec or loader for {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def run_graph_api_export():
    print('\n1) Running Graph API exporter to fetch posts...')
    # Load the module and use FacebookAnalyticsManager programmatically
    if not GRAPH_SCRIPT.exists():
        raise FileNotFoundError(f'Graph API script not found: {GRAPH_SCRIPT}')

    if str(WORKSPACE) not in sys.path:
        sys.path.insert(0, str(WORKSPACE))
    graph_dir = str(GRAPH_SCRIPT.parent)
    if graph_dir not in sys.path:
        sys.path.insert(0, graph_dir)

    graph_mod = load_module_from_path('get_posts_insights', GRAPH_SCRIPT)
    if not hasattr(graph_mod, 'FacebookAnalyticsManager'):
        raise RuntimeError('FacebookAnalyticsManager not found in Graph API module')

    manager = graph_mod.FacebookAnalyticsManager()
    raw_posts = manager.get_posts(limit=None)
    processed = manager.process_data(raw_posts)
    manager.export_to_json(processed, filename=str(FB_FULL_PATH))
    print(f'   Saved exporter output to: {FB_FULL_PATH}')
    return FB_FULL_PATH

def run_sort_posts():
    print('\n2) Running sort_posts.py to translate & sort posts...')
    if not SORT_SCRIPT.exists():
        raise FileNotFoundError(f'sort_posts.py not found: {SORT_SCRIPT}')
    subprocess.run([sys.executable, str(SORT_SCRIPT)], check=True)
    print(f'   Produced sorted posts at: {SORTED_PATH}')
    return SORTED_PATH

def run_preprocessing(input_path: Path):
    print('\n3) Running preprocessing on sorted posts...')
    if not PREPROCESS_MODULE.exists():
        raise FileNotFoundError(f'preprocessing.py not found: {PREPROCESS_MODULE}')
    pre_mod = load_module_from_path('preprocessing', PREPROCESS_MODULE)
    out = pre_mod.preprocess_context(str(input_path), None)
    print(f'   Preprocessed file: {out}')
    return Path(out)

def run_personatone(cleaned_path: Path, target_audience: str):
    print('\n4) Running persona analysis...')
    if not PERSONA_MODULE.exists():
        raise FileNotFoundError(f'personatone.py not found: {PERSONA_MODULE}')
    persona_mod = load_module_from_path('personatone', PERSONA_MODULE)

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        api_key = input('🔑 OpenAI key not found in env. Please enter it: ').strip()

    # 1. Load posts and check if they exist
    top_posts_text = persona_mod.load_top_posts(str(cleaned_path), top_n=10)
    
    # 2. Path branching: Posts vs No Posts
    if not top_posts_text.strip():
        print("\n⚠️ No historical posts found in the scraped data.")
        print("Please provide a 'template post' (an example of how you want your brand to sound).")
        input_text = input("   > ").strip()
        print(f"\n   Generating 3 Persona options from template post...")
    else:
        input_text = top_posts_text
        print(f"\n   Generating 3 Persona options from top performing posts...")

    # 3. Generate the 3 options
    persona_options = persona_mod.generate_persona_options(target_audience, input_text, api_key=api_key)
    
    # 4. Display options to the user
    print("\n" + "="*60)
    print("  🎯 SELECT YOUR PREFERRED BRAND PERSONA")
    print("="*60)
    
    for i, option in enumerate(persona_options.options, 1):
        print(f"\n[{i}] 🎭 ARCHETYPE: {option.archetype}")
        print(f"    🗣️ TONE: {option.emotional_tone}")
        print(f"    🔑 KEYWORDS: {', '.join(option.keywords)}")
        print(f"    📝 VOICE: {option.voice_description}")
        print("-" * 60)
        
    # 5. User Selection Loop
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
            
    # 6. Save the uniquely selected persona maintaining original JSON structure
    with open(str(FINAL_PERSONA_PATH), 'w', encoding='utf-8') as f:
        json.dump(selected_persona.model_dump(), f, ensure_ascii=False, indent=2)
        
    print(f'\n   ✅ Final persona saved to: {FINAL_PERSONA_PATH}')
    return FINAL_PERSONA_PATH

def main():
    print("="*60)
    print("  🎭 SOCIALIFT PERSONA PIPELINE")
    print("="*60)
    
    # Make the audience DYNAMIC
    target_audience = input("\n👥 Describe your Target Audience (e.g., 'Young professionals aged 25-35 interested in tech'):\n   > ").strip()
    
    if not target_audience:
        print("\n⚠️ No audience provided. Using generic fallback.")
        target_audience = "General audience interested in our brand."

    try:
        fb_path = run_graph_api_export()
        sorted_path = run_sort_posts()
        cleaned_path = run_preprocessing(sorted_path)
        final_path = run_personatone(cleaned_path, target_audience)
        
        print('\n' + '='*60)
        print('🎉 Persona Pipeline Complete!')
        print(f'📂 Final file: {final_path}')
        print('='*60)
        
    except subprocess.CalledProcessError as e:
        print('\n❌ A subprocess failed:', e)
    except Exception as e:
        print('\n❌ Pipeline failed:', e)

if __name__ == '__main__':
    main()
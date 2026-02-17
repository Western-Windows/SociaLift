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
    print('1) Running Graph API exporter to fetch posts...')
    # Load the module and use FacebookAnalyticsManager programmatically
    if not GRAPH_SCRIPT.exists():
        raise FileNotFoundError(f'Graph API script not found: {GRAPH_SCRIPT}')

    # Ensure workspace root is on sys.path so config imports work
    if str(WORKSPACE) not in sys.path:
        sys.path.insert(0, str(WORKSPACE))
    # Also ensure the Graph API folder is on sys.path so imports like `from config import Config` succeed
    graph_dir = str(GRAPH_SCRIPT.parent)
    if graph_dir not in sys.path:
        sys.path.insert(0, graph_dir)

    graph_mod = load_module_from_path('get_posts_insights', GRAPH_SCRIPT)
    if not hasattr(graph_mod, 'FacebookAnalyticsManager'):
        raise RuntimeError('FacebookAnalyticsManager not found in Graph API module')

    manager = graph_mod.FacebookAnalyticsManager()
    raw_posts = manager.get_posts(limit=None)
    processed = manager.process_data(raw_posts)
    # Export to fb_full_history.json in workspace root
    manager.export_to_json(processed, filename=str(FB_FULL_PATH))
    print(f'   Saved exporter output to: {FB_FULL_PATH}')
    return FB_FULL_PATH


def run_sort_posts():
    print('2) Running sort_posts.py to translate & sort posts...')
    if not SORT_SCRIPT.exists():
        raise FileNotFoundError(f'sort_posts.py not found: {SORT_SCRIPT}')
    # Run as a separate Python process to reuse its top-level script behavior
    subprocess.run([sys.executable, str(SORT_SCRIPT)], check=True)
    print(f'   Produced sorted posts at: {SORTED_PATH}')
    return SORTED_PATH


def run_preprocessing(input_path: Path):
    print('3) Running preprocessing on sorted posts...')
    if not PREPROCESS_MODULE.exists():
        raise FileNotFoundError(f'preprocessing.py not found: {PREPROCESS_MODULE}')
    pre_mod = load_module_from_path('preprocessing', PREPROCESS_MODULE)
    # Call function preprocess_context
    out = pre_mod.preprocess_context(str(input_path), None)
    print(f'   Preprocessed file: {out}')
    return Path(out)


def run_personatone(cleaned_path: Path):
    print('4) Running persona analysis...')
    if not PERSONA_MODULE.exists():
        raise FileNotFoundError(f'personatone.py not found: {PERSONA_MODULE}')
    persona_mod = load_module_from_path('personatone', PERSONA_MODULE)

    # Use defaults from personatone: audience & api key handling is inside
    audience = 'people with mental health challenges (15-30) and their support network'
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        print('OpenAI key not set in env; personatone will prompt if needed')

    persona = persona_mod.analyze_persona(audience, str(cleaned_path), api_key=api_key, top_n=10)
    # Save final persona JSON
    with open(str(FINAL_PERSONA_PATH), 'w', encoding='utf-8') as f:
        json.dump(persona.model_dump(), f, ensure_ascii=False, indent=2)
    print(f'   Final persona saved to: {FINAL_PERSONA_PATH}')
    return FINAL_PERSONA_PATH


def main():
    try:
        fb_path = run_graph_api_export()
        sorted_path = run_sort_posts()
        cleaned_path = run_preprocessing(sorted_path)
        final_path = run_personatone(cleaned_path)
        print('\nPipeline complete. Final file:' , final_path)
    except subprocess.CalledProcessError as e:
        print('A subprocess failed:', e)
    except Exception as e:
        print('Pipeline failed:', e)


if __name__ == '__main__':
    main()

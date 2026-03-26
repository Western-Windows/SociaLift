import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
load_dotenv()

# Import your graph builder and runner from the existing file
from enhan_graph import build_graph, run_interactive, EnhancementState

# Dynamically set the workspace to the folder containing 'Enhancement Module' (i.e., D:\SociaLift)
WORKSPACE = Path(__file__).resolve().parents[1]

PATHS = {
    "persona": WORKSPACE / "Persona Module" / "final_persona.json",
    "competitors": WORKSPACE / "Competitors Scraper" / "final_posts.json", 
    "holidays": WORKSPACE / "regional_events_holidays.json",
    "trends_google": WORKSPACE / "Graph API" / "filtered_trends_final.json", 
    "trends_x": WORKSPACE / "Graph API" / "trends_egypt_classified.json"
}

# ==========================================
# MASTER ORCHESTRATOR FUNCTIONS
# ==========================================

def run_script(script_path: Path):
    """Executes a python script using subprocess."""
    print(f"\n⏳ Running {script_path.name}...")
    if not script_path.exists():
        print(f"❌ Error: Script not found at {script_path}")
        return
    try:
        # Run the script, setting its current working directory to its own parent folder
        subprocess.run([sys.executable, str(script_path)], check=True, cwd=str(script_path.parent))
        print(f"✅ Finished {script_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run {script_path.name}. Error: {e}")
        
def run_all_prerequisites():
    """Runs all feeder pipelines to generate the required JSON files."""
    print("\n" + "="*60)
    print("🚀 GENERATING FRESH CONTEXT DATA")
    print("="*60)
    
    # 1. Graph API Trends & Holidays
    run_script(WORKSPACE / "Graph API" / "get_holidays.py")
    run_script(WORKSPACE / "Graph API" / "get_trends_google.py")
    run_script(WORKSPACE / "Graph API" / "get_trends_X.py")
    
    # 2. Persona Pipeline
    run_script(WORKSPACE / "Persona Module" / "persona_pipeline.py")
    
    # 3. Competitors Pipeline
    run_script(WORKSPACE / "Competitors Scraper" / "competitor_pipeline.py")
    run_script(WORKSPACE / "Competitors Scraper" / "process_all_posts.py")
    
    print("\n" + "="*60)
    print("✅ All prerequisite pipelines executed.")
    print("="*60 + "\n")
# ==========================================
# DATA LOADING FUNCTIONS
# ==========================================

def load_json_safe(filepath: Path) -> Any:
    """Safely load a JSON file, returning None if missing or invalid."""
    if not filepath.exists():
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def extract_list_dynamically(data: Any) -> List[Any]:
    """Universally normalizes JSON data into a list."""
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for common_key in ["data", "trends", "holidays", "results", "posts", "items"]:
            if common_key in data and isinstance(data[common_key], list):
                return data[common_key]
        for value in data.values():
            if isinstance(value, list):
                return value
        return [data]
    return []

def extract_dict_dynamically(data: Any) -> Dict[str, Any]:
    """Universally normalizes JSON data into a flat dictionary for the persona."""
    if not data or not isinstance(data, dict):
        return {}
    expected_keys = {"archetype", "emotional_tone", "keywords", "voice_description"}
    if any(k in data for k in expected_keys):
        return data
    for common_key in ["persona", "data", "result", "brand_persona"]:
        if common_key in data and isinstance(data[common_key], dict):
            return data[common_key]
    for value in data.values():
        if isinstance(value, dict):
            return value
    return data

def build_initial_state() -> EnhancementState:
    """Constructs the initial state using dynamic extraction."""
    print("📥 Loading contextual data dynamically...")
    
    persona_data = extract_dict_dynamically(load_json_safe(PATHS["persona"]))
    competitors_data = extract_list_dynamically(load_json_safe(PATHS["competitors"]))
    holidays_data    = extract_list_dynamically(load_json_safe(PATHS["holidays"]))
    google_trends    = extract_list_dynamically(load_json_safe(PATHS["trends_google"]))
    x_trends         = extract_list_dynamically(load_json_safe(PATHS["trends_x"]))
    
    print(f"   ✓ Persona Attributes Found: {list(persona_data.keys()) if persona_data else 'None'}")
    print(f"   ✓ Competitor posts found: {len(competitors_data)}")
    print(f"   ✓ Holidays found: {len(holidays_data)}")
    print(f"   ✓ Google Trends found: {len(google_trends)}")
    print(f"   ✓ X Trends found: {len(x_trends)}")

    state: EnhancementState = {
        "persona": persona_data,
        "competitors_data": competitors_data,
        "holidays_trends": {
            "holidays": holidays_data,
            "google_trends": google_trends,
            "x_trends": x_trends
        },
        "mode": None,
        "input_type": None,
        "raw_input": None,
        "generated_post": None,
        "action": None,
        "action_input": None,
        "final_post": None
    }
    return state

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    # 1. Ask the user if they want to run the pipelines to generate the files
    missing_files = [name for name, path in PATHS.items() if not path.exists()]
    
    if missing_files:
        print(f"\n⚠️ Missing files detected: {', '.join(missing_files)}")
        ans = input("Do you want to run the pipelines to generate them now? (y/n): ").strip().lower()
        if ans == 'y':
            run_all_prerequisites()
    else:
        ans = input("\nAll data files found. Do you want to refresh them by re-running the pipelines? (y/n): ").strip().lower()
        if ans == 'y':
            run_all_prerequisites()

    # 2. Build the state and run the LangGraph
    initial_state = build_initial_state()
    
    graph = build_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "session-live"}}
    
    run_interactive(graph, config, initial_state)
    
    # 3. Save output
    final_state = graph.get_state(config)
    if final_state and final_state.values.get("final_post"):
        final_post = final_state.values["final_post"]
        output_path = WORKSPACE / "Enhancement Module" / "enhanced_post_result.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"enhanced_post": final_post}, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 Enhanced post saved to {output_path}")

if __name__ == "__main__":
    main() 
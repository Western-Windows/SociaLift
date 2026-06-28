"""
Post Enhancement Module using LangGraph

Upfront questions (via interrupts):
  1. Mode:       auto (just generate, no review) OR manual (update/edit/confirm loop)
  2. Input type: idea (generate from scratch)    OR post  (rephrase existing)
  3. Text:       the actual idea or post

Then:
  auto   → generate/rephrase → done ✅
  manual → generate/rephrase → update | edit | confirm loop
"""

import os
from pathlib import Path
from typing import TypedDict, List, Optional, Any, Dict, Literal
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import SecretStr



# -------------------- State --------------------
class EnhancementState(TypedDict):
    persona: Dict[str, Any]
    competitors_data: List[Dict[str, Any]]
    holidays_trends: Dict[str, Any]                 # Updated to Dict to hold all trends together

    mode: Optional[Literal["auto", "manual"]]       # chosen by user
    input_type: Optional[Literal["idea", "post"]]   # chosen by user
    raw_input: Optional[str]                         # text entered by user

    generated_post: Optional[str]
    action: Optional[str]
    action_input: Optional[str]
    final_post: Optional[str]


# -------------------- LLM --------------------
def get_llm():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenAI API key: ").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required.")
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=SecretStr(api_key))

llm = get_llm()


# -------------------- Helpers --------------------
def _persona_block(persona: Dict[str, Any]) -> str:
    return (
        f"- Archetype: {persona.get('archetype', 'N/A')}\n"
        f"- Tone: {persona.get('emotional_tone', 'N/A')}\n"
        f"- Keywords: {', '.join(persona.get('keywords', []))}\n"
        f"- Voice: {persona.get('voice_description', 'N/A')}"
    )

def _extract_text(response) -> str:
    content = response.content
    if isinstance(content, list):
        return " ".join(str(i) for i in content if isinstance(i, str))
    return content


# -------------------- Node: ask all upfront questions --------------------
def ask_setup(state: EnhancementState) -> dict:
    """Ask mode, input type, and text — all before any generation."""
    print("\n🔵 NODE: ask_setup")

    # If already provided in state (e.g. via API), skip interactive prompts
    if state.get("mode") and state.get("input_type") and state.get("raw_input"):
        print(f"  Mode: {state['mode']!r}")
        print(f"  Input type: {state['input_type']!r}")
        print(f"  Raw input: {state['raw_input'][:80]!r}...")
        return {"mode": state["mode"], "input_type": state["input_type"], "raw_input": state["raw_input"]}

    # Q1 — mode
    mode_answer = interrupt({
        "message": (
            "How would you like to work?\n"
            "  auto   — generate and done, no review needed\n"
            "  manual — I want to review, update, edit, then confirm\n"
        )
    })
    mode: Literal["auto", "manual"] = "auto" if "auto" in str(mode_answer).strip().lower() else "manual"
    print(f"  Mode: {mode!r}")

    # Q2 — input type
    type_answer = interrupt({
        "message": (
            "Is your input an idea or an existing post?\n"
            "  idea — I have a topic/theme, generate a post for me\n"
            "  post — I have a written post, rephrase/enhance it\n"
        )
    })
    input_type: Literal["idea", "post"] = "post" if "post" in str(type_answer).strip().lower() else "idea"
    print(f"  Input type: {input_type!r}")

    # Q3 — the actual text
    prompt_message = "Enter your idea or topic:" if input_type == "idea" else "Paste your existing post:"
    raw = interrupt({"message": prompt_message})
    raw = str(raw).strip()
    print(f"  Raw input: {raw[:80]!r}...")

    return {"mode": mode, "input_type": input_type, "raw_input": raw}


# -------------------- Node: generate from idea --------------------
def generate_from_idea(state: EnhancementState) -> dict:
    print("\n🟢 NODE: generate_from_idea")
    persona = state.get("persona", {})
    
    # Format Competitors
    comp_text = "\n".join(
        f"- {c.get('context', '')[:200]}"
        for c in state.get("competitors_data", [])[:5] if isinstance(c, dict) and c.get("context")
    ) or "No competitor data."
    
    # Format Holidays & Trends
    ht_data = state.get("holidays_trends", {})
    holidays = ht_data.get("holidays", [])[:3]
    g_trends = ht_data.get("google_trends", [])[:3]
    x_trends = ht_data.get("x_trends", [])[:3]
    
    context_text = ""
    if holidays:
        context_text += "**Upcoming Holidays:**\n" + "\n".join(f"- {h.get('name', h.get('holiday_name'))} ({h.get('date')})" for h in holidays) + "\n\n"
    if g_trends:
        context_text += "**Google Trends:**\n" + "\n".join(f"- {t.get('title', t)}" for t in g_trends) + "\n\n"
    if x_trends:
        context_text += "**X (Twitter) Trends:**\n" + "\n".join(f"- {t.get('name', t)}" for t in x_trends) + "\n"
        
    if not context_text:
        context_text = "No current holidays or trends provided."

    prompt = f"""You are a social media content creator. Write a post based on:

**Brand Persona**
{_persona_block(persona)}

**User idea:** "{state['raw_input']}"

**Competitor inspiration (Analyze their tone, but do NOT copy them directly):**
{comp_text}

**Current Context (Incorporate subtly if relevant to the user idea):**
{context_text}

Write an engaging social media post that matches the brand persona. Output only the post text.
"""
    response = llm.invoke([
        SystemMessage("You are a creative social media copywriter."),
        HumanMessage(prompt)
    ])
    content = _extract_text(response)
    print("✅ Post generated from idea.")
    return {"generated_post": content, "action": None, "action_input": None}


# -------------------- Node: rephrase existing post --------------------
def rephrase_existing_post(state: EnhancementState) -> dict:
    print("\n🟣 NODE: rephrase_existing_post")
    persona = state.get("persona", {})

    prompt = f"""You are a social media copywriter. Rephrase and enhance the following post
to better match the brand persona below, while preserving the original meaning and intent.

**Brand Persona**
{_persona_block(persona)}

**Original post:**
\"\"\"{state['raw_input']}\"\"\"

Output only the rephrased post text.
"""
    response = llm.invoke([
        SystemMessage("You are a creative social media copywriter."),
        HumanMessage(prompt)
    ])
    content = _extract_text(response)
    print("✅ Post rephrased.")
    return {"generated_post": content, "action": None, "action_input": None}


# -------------------- Node: auto finalize (no review) --------------------
def auto_finalize(state: EnhancementState) -> dict:
    print("\n⚡ NODE: auto_finalize — skipping review")
    return {"final_post": state["generated_post"]}


# -------------------- Node: ask user what to do (manual loop) --------------------
def ask_user(state: EnhancementState) -> dict:
    print("\n🟡 NODE: ask_user")
    response = interrupt({
        "post": state["generated_post"],
        "message": (
            "What would you like to do?\n"
            "  update  — give feedback, AI rewrites\n"
            "  edit    — type your own version\n"
            "  confirm — finalize the post\n"
        )
    })
    parts = response.strip().split(None, 1)
    action = parts[0].lower() if parts else ""
    action_input = parts[1].strip() if len(parts) > 1 else ""
    print(f"  Action: {action!r}  |  Input: {action_input!r}")
    return {"action": action, "action_input": action_input}


# -------------------- Node: update (AI rewrite) --------------------
def do_update(state: EnhancementState) -> dict:
    print("\n🟢 NODE: do_update")
    feedback = state["action_input"]
    if not feedback:
        feedback = interrupt({
            "post": state["generated_post"],
            "message": "Describe how you want the post updated:"
        })
        feedback = str(feedback).strip()

    persona = state.get("persona", {})
    prompt = f"""Revise this social media post based on the feedback below.
Keep the brand persona:
{_persona_block(persona)}

**Current post:**
{state['generated_post']}

**Feedback:** "{feedback}"

Output only the revised post text.
"""
    response = llm.invoke([
        SystemMessage("You are a social media copywriter refining a post."),
        HumanMessage(prompt)
    ])
    content = _extract_text(response)
    print("✅ Post updated by AI.")
    return {"generated_post": content, "action": None, "action_input": None}


# -------------------- Node: edit (user replaces text) --------------------
def do_edit(state: EnhancementState) -> dict:
    print("\n🟠 NODE: do_edit")
    new_text = state["action_input"]
    if not new_text:
        new_text = interrupt({
            "post": state["generated_post"],
            "message": "Paste or type your edited version of the post:"
        })
        new_text = str(new_text).strip()

    result = new_text if new_text else state["generated_post"]
    print("✅ Post replaced with user edit.")
    return {"generated_post": result, "action": None, "action_input": None}


# -------------------- Node: confirm --------------------
def do_confirm(state: EnhancementState) -> dict:
    print("\n✅ NODE: do_confirm")
    return {"final_post": state["generated_post"]}


# -------------------- Routing --------------------

def route_input_type(state: EnhancementState) -> Literal["generate_from_idea", "rephrase_existing_post"]:
    return "generate_from_idea" if state.get("input_type") == "idea" else "rephrase_existing_post"

def route_after_generation(state: EnhancementState) -> Literal["auto_finalize", "ask_user"]:
    return "auto_finalize" if state.get("mode") == "auto" else "ask_user"

def route_action(state: EnhancementState) -> Literal["do_update", "do_edit", "do_confirm", "ask_user"]:
    action = (state.get("action") or "").lower()
    if action in ("update", "u"):           return "do_update"
    elif action in ("edit", "e"):           return "do_edit"
    elif action in ("confirm", "c", "yes"): return "do_confirm"
    else:
        print(f"  ⚠️  Unknown action '{action}', asking again.")
        return "ask_user"


# -------------------- Graph --------------------
def build_graph():
    builder = StateGraph(EnhancementState)

    builder.add_node("ask_setup",             ask_setup)
    builder.add_node("generate_from_idea",    generate_from_idea)
    builder.add_node("rephrase_existing_post",rephrase_existing_post)
    builder.add_node("auto_finalize",         auto_finalize)
    builder.add_node("ask_user",              ask_user)
    builder.add_node("do_update",             do_update)
    builder.add_node("do_edit",               do_edit)
    builder.add_node("do_confirm",            do_confirm)

    builder.set_entry_point("ask_setup")

    # Route: idea vs post
    builder.add_conditional_edges("ask_setup", route_input_type, {
        "generate_from_idea":     "generate_from_idea",
        "rephrase_existing_post": "rephrase_existing_post",
    })

    # After generation: auto → finalize, manual → review loop
    builder.add_conditional_edges("generate_from_idea", route_after_generation, {
        "auto_finalize": "auto_finalize",
        "ask_user":      "ask_user",
    })
    builder.add_conditional_edges("rephrase_existing_post", route_after_generation, {
        "auto_finalize": "auto_finalize",
        "ask_user":      "ask_user",
    })

    # Auto path ends immediately
    builder.add_edge("auto_finalize", END)

    # Manual review loop
    builder.add_conditional_edges("ask_user", route_action, {
        "do_update":  "do_update",
        "do_edit":    "do_edit",
        "do_confirm": "do_confirm",
        "ask_user":   "ask_user",
    })
    builder.add_edge("do_update",  "ask_user")
    builder.add_edge("do_edit",    "ask_user")
    builder.add_edge("do_confirm", END)

    return builder.compile(checkpointer=MemorySaver())


# -------------------- Runner --------------------
def get_pending_interrupt(graph, config):
    state = graph.get_state(config)
    if state.tasks and state.tasks[0].interrupts:
        return state.tasks[0].interrupts[0].value
    return None


def run_interactive(graph, config, initial_state):
    print("\n🚀 Starting graph...")
    for _ in graph.stream(initial_state, config, stream_mode="values"):
        pass

    while True:
        iv = get_pending_interrupt(graph, config)
        if iv is None:
            break

        print("\n" + "=" * 60)
        if "post" in iv:
            print(iv["post"])
            print("-" * 60)
        user_response = input(f"\n{iv.get('message', 'Input:')}\n> ").strip()

        for _ in graph.stream(Command(resume=user_response), config, stream_mode="values"):
            pass


if __name__ == "__main__":
    # Test block with mock data structured exactly like the real pipeline
    sample_persona = {
        "archetype": "The Celebrant",
        "emotional_tone": "High (Warm & Festive)",
        "keywords": ["Eid", "blessings", "family", "gratitude", "joy", "togetherness"],
        "voice_description": "Joyful, heartfelt, and celebratory. Speaks with warmth and spiritual sincerity."
    }

    graph = build_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "session-test"}}

    initial_state: EnhancementState = {
        "persona": sample_persona,
        "competitors_data": [
            {"context": "Wishing you and your family a blessed Eid full of joy, love, and togetherness. Eid Mubarak! 🌙"},
            {"context": "May this Eid bring peace to your heart and happiness to your home. Celebrate with gratitude and love. ✨"}
        ],
        "holidays_trends": {
            "holidays": [{"holiday_name": "Eid El Fitr", "date": "2025-03-30"}],
            "google_trends": [{"title": "Eid prayers schedule"}, {"title": "Best Eid desserts"}],
            "x_trends": [{"name": "#EidMubarak"}, {"name": "#Celebrate"}]
        },
        "mode": None,
        "input_type": None,
        "raw_input": None,
        "generated_post": None,
        "action": None,
        "action_input": None,
        "final_post": None
    }

    run_interactive(graph, config, initial_state)

    final_state = graph.get_state(config)
    final_post = final_state.values.get("final_post") if final_state else None

    print("\n" + "=" * 60)
    print("🎉 FINAL POST:")
    print(final_post or "No post generated.")
    print("=" * 60)
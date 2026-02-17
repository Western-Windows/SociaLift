from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
import json
import os

class PersonaTone(BaseModel):
    archetype: str = Field(description="the marketing archetype that best describes the persona(e.g. the caregiver, the creator, the jester, etc.)")
    emotional_tone: str = Field(description="Low(Calm), Medium(Conversational), High(Excited)")
    keywords: List[str] = Field(description="5 dominant words or themes found in the posts")
    voice_description: str = Field(description="a description of the voice and tone of the persona, including any specific language or stylistic choices that should be used when writing for this persona")
    
parser = PydanticOutputParser(pydantic_object=PersonaTone)


template =""" 
You are a Brand Strategist, analyze the following inputs to reverse-engineer the brand persona and tone of voice.

TARGET AUDIENCE: {audience}
TOP PERFORMING POSTS: {top_posts}

TASK:
Ignore the specific content(e.g. the product or service being marketed) and focus on the underlying tone, style, and emotional resonance of the posts. Based on your analysis, provide a detailed description of the brand persona and tone of voice that would be most effective in engaging the target audience.
{format_instructions}

"""


prompt = PromptTemplate(
    template  = template,
    input_variables = ['audience', 'top_posts'],
    partial_variables = {"format_instructions": parser.get_format_instructions()}
)


def load_top_posts(json_path, top_n=10):
    """Load top N posts from the cleaned JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Support two shapes:
    # 1) list of {"reaction_count", "context"} (legacy)
    # 2) exporter format from `get_posts_insights.py`: {"metadata":..., "data": [ {post objects} ]}
    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict) and 'data' in data:
        posts = data['data']
    else:
        raise ValueError("Unrecognized posts JSON structure")

    # Normalize posts to a common structure: reaction_count (int) and context (text)
    normalized = []
    for p in posts:
        # Legacy keys
        if isinstance(p, dict) and 'reaction_count' in p and 'context' in p:
            rc = p.get('reaction_count', 0)
            ctx = p.get('context', '')
        else:
            # Try Graph API exporter shape
            eng = p.get('engagement_stats', {}) if isinstance(p, dict) else {}
            rc = eng.get('likes') or eng.get('like_count') or 0
            ctx = p.get('message') or p.get('context') or ''

        try:
            rc = int(rc)
        except Exception:
            rc = 0

        normalized.append({
            'reaction_count': rc,
            'context': ctx
        })

    # Sort by reaction_count desc and pick top_n
    top_posts = sorted(normalized, key=lambda x: x['reaction_count'], reverse=True)[:top_n]

    # Format posts for the prompt
    formatted_posts = []
    for i, post in enumerate(top_posts, 1):
        formatted_posts.append(f"Post {i} ({post['reaction_count']} reactions):\n{post['context']}")

    return "\n\n".join(formatted_posts)


def analyze_persona(audience: str, posts_json_path: str, api_key: str, top_n: int = 10) -> PersonaTone:
    """
    Analyze the brand persona and tone from top performing posts.
    
    Args:
        audience: Description of the target audience
        posts_json_path: Path to the cleaned posts JSON file
        api_key: OpenAI API key (optional, uses env var if not provided)
        top_n: Number of top posts to analyze
    
    Returns:
        PersonaTone object with the analyzed persona
    """
    # Load top posts
    top_posts = load_top_posts(posts_json_path, top_n)
    
    # Initialize LLM
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    # Create chain
    chain = prompt | llm | parser
    
    # Run analysis
    result = chain.invoke({
        "audience": audience,
        "top_posts": top_posts
    })
    
    return result


def save_persona(persona: PersonaTone, output_path: str):
    """Save the persona analysis to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(persona.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Persona saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    audience = "sucidial people with mental issues age from 15 to 30 years old and their family members and friends"
    posts_path = "d:/SociaLift/sorted_posts_cleaned.json"
    api = ""
    # Set your API key here or as environment variable
    os.environ["OPENAI_API_KEY"] = "" 
    
    try:
        persona = analyze_persona(audience, posts_path, api_key=api, top_n=10)
        print("\n=== PERSONA ANALYSIS ===")
        print(f"Archetype: {persona.archetype}")
        print(f"Emotional Tone: {persona.emotional_tone}")
        print(f"Keywords: {', '.join(persona.keywords)}")
        print(f"\nVoice Description:\n{persona.voice_description}")
        
        # Save to file
        save_persona(persona, "d:/SociaLift/persona_analysis.json")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your OPENAI_API_KEY environment variable")
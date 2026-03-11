from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
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

class PersonaOptions(BaseModel):
    options: List[PersonaTone] = Field(description="Exactly 3 distinct persona options based on the input text.")
    
parser = PydanticOutputParser(pydantic_object=PersonaOptions)

template =""" 
You are a Brand Strategist. Analyze the following inputs to reverse-engineer and suggest 3 distinct brand personas and tones of voice.

TARGET AUDIENCE: {audience}
INPUT TEXT: {input_text}

TASK:
Based on the INPUT TEXT (which may be historical posts or a template post), generate 3 distinct but highly effective brand persona options that would engage the TARGET AUDIENCE. 
Ensure the 3 archetypes and emotional tones are noticeably different from each other to give the user good variety.
{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=['audience', 'input_text'],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def load_top_posts(json_path, top_n=10):
    """Load top N posts from the cleaned JSON file. Returns empty string if no posts."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

    if isinstance(data, list):
        posts = data
    elif isinstance(data, dict) and 'data' in data:
        posts = data['data']
    else:
        return ""

    if not posts:
        return ""

    normalized = []
    for p in posts:
        if isinstance(p, dict) and 'reaction_count' in p and 'context' in p:
            rc = p.get('reaction_count', 0)
            ctx = p.get('context', '')
        else:
            eng = p.get('engagement_stats', {}) if isinstance(p, dict) else {}
            rc = eng.get('likes') or eng.get('like_count') or 0
            ctx = p.get('message') or p.get('context') or ''

        try:
            rc = int(rc)
        except Exception:
            rc = 0

        normalized.append({'reaction_count': rc, 'context': ctx})

    top_posts = sorted(normalized, key=lambda x: x['reaction_count'], reverse=True)[:top_n]

    formatted_posts = []
    for i, post in enumerate(top_posts, 1):
        if post['context'].strip():
            formatted_posts.append(f"Post {i} ({post['reaction_count']} reactions):\n{post['context']}")

    return "\n\n".join(formatted_posts)

def generate_persona_options(audience: str, input_text: str, api_key: str) -> PersonaOptions:
    """Generate 3 persona options based on the audience and input text."""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    chain = prompt | llm | parser
    
    result = chain.invoke({
        "audience": audience,
        "input_text": input_text
    })
    
    return result

def save_persona(persona: PersonaTone, output_path: str):
    """Save the persona analysis to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(persona.model_dump(), f, ensure_ascii=False, indent=2)
    print(f"Persona saved to: {output_path}")
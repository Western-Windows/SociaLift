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
    """Load top N posts from the cleaned JSON file. Assumes data is already sorted."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return ""

    posts = data.get('data', data) if isinstance(data, dict) else data
    
    if not posts or not isinstance(posts, list):
        return ""

    formatted_posts = []
    valid_count = 0
    
    # Data is already sorted by sort_posts.py, so we just take the first top_n valid posts
    for post in posts:
        if valid_count >= top_n:
            break
            
        rc = post.get('reaction_count', 0)
        ctx = post.get('context', '').strip()
        
        if ctx:
            formatted_posts.append(f"Post {valid_count + 1} ({rc} reactions):\n{ctx}")
            valid_count += 1

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
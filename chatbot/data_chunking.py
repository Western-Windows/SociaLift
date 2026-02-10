import pandas as pd
import json
import os
import getpass
import ast
from dotenv import load_dotenv
from pathlib import Path
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, SystemMessage

class UniversalRAGIngestor:
    def __init__(self, df, name_col, desc_col=None):
        self.df = df
        self.name_col = name_col
        self.desc_col = desc_col
        # NOTE: We no longer calculate meta_cols here. 
        # We will do it dynamically in process().

    def _get_llm(self):
        """Helper to initialize the LLM client securely."""

        load_dotenv()
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        print(os.environ["HUGGINGFACEHUB_API_TOKEN"][:5] + "..." + os.environ["HUGGINGFACEHUB_API_TOKEN"][-5:])
        # Consistent model config
        HF_MODELS = [
            "meta-llama/Llama-3.1-8B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
            "mistralai/Mistral-Nemo-Instruct-2407",
            "deepseek-ai/DeepSeek-R1",
        ]
        HF_MODEL_ID = os.environ.get("HF_MODEL_ID", HF_MODELS[0])
        
        llm_endpoint = HuggingFaceEndpoint(
            repo_id=HF_MODEL_ID,
            task="text-generation",
            max_new_tokens=4096,
            temperature=0.1, # Lower temp for logic tasks like column selection
            top_p=0.95,
            return_full_text=False,
        )
        return ChatHuggingFace(llm=llm_endpoint)

    def _call_agent_for_metadata_selection(self, sample_data):
        """
        Asks the LLM to identify which columns are important for filtering.
        Input: Data sample.
        Output: A python list of column names (e.g., ['Gender', 'Category']).
        """
        model = self._get_llm()
        all_cols = list(sample_data[0].keys()) if sample_data else []

        prompt = f"""
        You are a Data Engineer. 
        Here is a sample of dataset columns and values: 
        {json.dumps(sample_data)}

        Task: Identify which columns represents useful "Metadata" (facets, categories, tags, pricing, grouping).
        
        Rules:
        1. EXCLUDE unique IDs (like 'ProductId', 'UUID').
        2. EXCLUDE URLs or Image links.
        3. EXCLUDE the primary name column: '{self.name_col}'.
        4. INCLUDE categorical fields (Gender, Color, Cuisine) or metrics (Price, Rating).
        5. Return ONLY a valid Python list of strings. No markdown, no explanation.

        Example Output: ['Color', 'Size', 'Brand']
        """

        messages = [
            SystemMessage(content="You extract metadata schema from data. Output only a Python list."),
            HumanMessage(content=prompt)
        ]

        try:
            result = model.invoke(messages)
            clean_text = result.content.strip()
            
            # Cleanup Markdown/Chatter
            clean_text = clean_text.replace("```python", "").replace("```", "").strip()
            if "[" in clean_text:
                start = clean_text.find("[")
                end = clean_text.rfind("]") + 1
                clean_text = clean_text[start:end]

            # Parse string to list
            selected_cols = ast.literal_eval(clean_text)
            
            # Validate columns actually exist
            valid_cols = [c for c in selected_cols if c in self.df.columns]
            return valid_cols

        except Exception as e:
            print(f"⚠ Metadata Agent failed: {e}. Falling back to all columns.")
            # Fallback: All columns except Name/Desc
            exclude = [self.name_col, self.desc_col] if self.desc_col else [self.name_col]
            return [c for c in self.df.columns if c not in exclude]

    def _call_agent_for_template(self, sample_data):
        """
        Asks the LLM to write a sentence template.
        """
        model = self._get_llm()
        keys_example = list(sample_data[0].keys()) if sample_data else []
        
        prompt = f"""
        Data Sample: {json.dumps(sample_data)}
        
        Task: Create a natural language sentence template to describe this data item.
        Use Python .format() notation (curly braces) for column names.
        
        Example Input: [{{"Name": "Nike Air", "Color": "Red"}}]
        Example Output: The product {{Name}} comes in the color {{Color}}.

        Return ONLY the template string.
        """
        
        messages = [
            SystemMessage(content="You are a data processing engine. Output raw text templates only."),
            HumanMessage(content=prompt)
        ]

        try:
            result = model.invoke(messages)
            clean_text = result.content.strip().replace("```", "").strip()
            if (clean_text.startswith('"') and clean_text.endswith('"')): clean_text = clean_text[1:-1]
            return clean_text
        except Exception:
            return f"{{ {self.name_col} }}"

    def process(self):
        # Sample data for the agents
        sample = self.df.head(3).to_dict(orient='records')

        # --- STEP 1: Determine Metadata Schema (LLM) ---
        print("🤖 Analyzing columns for importance...")
        self.meta_cols = self._call_agent_for_metadata_selection(sample)
        print(f"✔ Selected Metadata Columns: {self.meta_cols}")

        # --- STEP 2: Determine Text Template (LLM or Static) ---
        if self.desc_col and self.desc_col in self.df.columns:
            print("✔ Description column found. Using existing text.")
            template = None
        else:
            print("🤖 Asking Agent to generate a description template...")
            template = self._call_agent_for_template(sample)
            print(f"✔ Template: \"{template}\"")

        # --- STEP 3: Generate Rows ---
        results = []
        for idx, row in self.df.iterrows():
            # Filter Metadata based on LLM selection
            metadata = {col: row[col] for col in self.meta_cols if pd.notna(row[col])}
            
            # Generate Text
            if template:
                try:
                    text_to_embed = template.format(**row.to_dict())
                except KeyError:
                    text_to_embed = f"{row[self.name_col]}"
            else:
                text_to_embed = f"{row[self.name_col]}. {row[self.desc_col]}"

            results.append({
                "id": str(idx),
                "text": text_to_embed,
                "metadata": metadata
            })
            
        return results
    
csv_path = Path("chatbot/fashion.csv")

df = pd.read_csv(csv_path)

print(UniversalRAGIngestor(df, "ProductTitle").process())
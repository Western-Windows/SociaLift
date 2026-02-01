import pandas as pd
import json
import os
import getpass
from pathlib import Path
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, SystemMessage

class UniversalRAGIngestor:
    def __init__(self, df, name_col, desc_col=None):
        self.df = df
        self.name_col = name_col
        self.desc_col = desc_col
        
        # 1. Identify Metadata Columns (Everything that isn't Name or Desc)
        exclude = [self.name_col,'ProductId','ImageURL']
        if self.desc_col:
            exclude.append(self.desc_col)
        self.meta_cols = [c for c in df.columns if c not in exclude]

    def _call_agent_for_template(self, sample_data):
        """
        Simulates an LLM call.
        Input: A sample of the data (headers and 2-3 rows).
        Output: A Python f-string template.
        """

        os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not os.environ.get("HUGGINGFACEHUB_API_TOKEN"):
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass.getpass(
                "Enter Hugging Face token (HUGGINGFACEHUB_API_TOKEN): "
            )

        # Allowed model list
        HF_MODELS = [
            "meta-llama/Llama-3.1-8B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct",
            "mistralai/Mistral-Nemo-Instruct-2407",
            "deepseek-ai/DeepSeek-R1",
        ]

        HF_MODEL_ID = os.environ.get("HF_MODEL_ID", HF_MODELS[0])
        if HF_MODEL_ID not in HF_MODELS:
            raise ValueError(f"HF_MODEL_ID must be one of {HF_MODELS}. Got: {HF_MODEL_ID!r}")

        HF_PROVIDER = os.environ.get("HF_PROVIDER", "auto")
        HF_MAX_NEW_TOKENS = int(os.environ.get("HF_MAX_NEW_TOKENS", "4096"))
        HF_TEMPERATURE = float(os.environ.get("HF_TEMPERATURE", "0.5"))
        HF_TOP_P = float(os.environ.get("HF_TOP_P", "0.95"))

        # Endpoint for agent: text-generation + ChatHuggingFace wrapper
        llm_agent = HuggingFaceEndpoint(
            repo_id=HF_MODEL_ID,
            task="text-generation",
            provider=HF_PROVIDER,
            max_new_tokens=HF_MAX_NEW_TOKENS,
            temperature=HF_TEMPERATURE,
            top_p=HF_TOP_P,
            return_full_text=False,
        )
        model = ChatHuggingFace(llm=llm_agent)

        keys_example = list(sample_data[0].keys()) if sample_data else []
        # IN PRODUCTION: You would send this prompt to GPT-4/Claude/Gemini
        prompt = f"""
        Here is a sample of structured data: {json.dumps(sample_data)}

        Task: Create a single sentence template to describe this data.
        
        Strict Output Rules:
        1. Use Python .format() notation: use curly braces wrapping the exact column names. Example: "{{{keys_example[0]}}}".
        2. DO NOT use python code, f-strings, or "row['col']" syntax. Just the column name inside braces.
        3. DO NOT wrap the output in markdown code blocks (no ```).
        4. Return ONLY the template string. No "Here is the template", no explanations.
        
        Example Input: [{{"Name": "Nike Air", "Color": "Red"}}]
        Example Output: The product {{Name}} comes in the color {{Color}}.
        """
        # 2. FIXED: Create a list of Message objects
        messages = [
            SystemMessage(content="You are a data processing engine. You output raw text templates only."),
            HumanMessage(content=prompt)
        ]

        try:
            result = model.invoke(messages)
            raw_content = result.content.strip()

            # 2. ROBUST CLEANUP: Remove common "chatty" artifacts
            
            # Remove markdown code blocks if they appear
            clean_text = raw_content.replace("```python", "").replace("```", "").strip()
            
            # Remove generic "Here is the code" prefixes if the LLM ignores instructions
            if ":" in clean_text and len(clean_text.split(":")[0]) < 50:
                 # heuristic: if there is a colon early on, take everything after it
                 clean_text = clean_text.split(":", 1)[1].strip()

            # Remove surrounding quotes (often LLMs return "The template")
            if (clean_text.startswith('"') and clean_text.endswith('"')) or \
               (clean_text.startswith("'") and clean_text.endswith("'")):
                clean_text = clean_text[1:-1]

            # 3. SAFETY CHECK: Ensure braces exist (otherwise it's not a template)
            if "{" not in clean_text or "}" not in clean_text:
                # Fallback if LLM failed to make a template
                print("⚠ Agent failed to generate valid template brackets. Using default.")
                return f"{{ {self.name_col} }}"

            return clean_text
        except Exception as e:
            print(f"Error calling agent: {e}")
            return None

    def process(self):
        # Step 1: Determine the Strategy
        if self.desc_col and self.desc_col in self.df.columns:
            print("✔ Description column found. Using existing text.")
            template = None
        else:
            print("⚠ No description found. Asking Agent to create a template...")
            # Take a small sample to show the Agent
            sample = self.df[[self.name_col] + self.meta_cols].head(3).to_dict(orient='records')
            template = self._call_agent_for_template(sample)
            print(f"✔ Agent created template: \"{template}\"")

        # Step 2: Process Rows
        results = []
        for idx, row in self.df.iterrows():
            # A. Prepare Metadata
            metadata = {col: row[col] for col in self.meta_cols if pd.notna(row[col])}
            
            # B. Generate Text
            if template:
                # Fill the Agent's template with this row's data
                # .format(**row) maps column names to {ColumnName} in the string
                try:
                    text_to_embed = template.format(**row.to_dict())
                except KeyError:
                    # Fallback if a column is missing in a specific row
                    text_to_embed = f"{row[self.name_col]}"
            else:
                # Use existing description
                text_to_embed = f"{row[self.name_col]}. {row[self.desc_col]}"

            # C. Build Record
            results.append({
                "id": str(idx), # Or use a real ID column
                "text": text_to_embed,
                "metadata": metadata
            })
            
        return results


csv_path = Path("chatbot/fashion.csv")

df = pd.read_csv(csv_path)

print(UniversalRAGIngestor(df, "ProductTitle").process())

# # --- DEMO: SCENARIO 1 (E-Commerce, No Description) ---
# data_clothes = {
#     "ProductTitle": ["Nike Air", "Adidas Top"],
#     "Gender": ["Men", "Women"],
#     "Colour": ["Red", "Blue"],
#     "Usage": ["Running", "Casual"]
# }
# df1 = pd.DataFrame(data_clothes)

# print("--- Processing Clothes (No Description) ---")
# ingestor1 = UniversalRAGIngestor(df1, name_col="ProductTitle") # No desc_col provided
# vectors1 = ingestor1.process()
# print("Result 1:", vectors1[0]['text'])
# print("-" * 30)

# # --- DEMO: SCENARIO 2 (Restaurants, No Description) ---
# data_food = {
#     "Name": ["Joe's Pizza", "Sushi World"],
#     "Cuisine": ["Italian", "Japanese"],
#     "Neighborhood": ["Downtown", "Uptown"],
#     "Price": ["$$", "$$$"]
# }
# df2 = pd.DataFrame(data_food)

# print("--- Processing Restaurants (No Description) ---")
# ingestor2 = UniversalRAGIngestor(df2, name_col="Name")
# vectors2 = ingestor2.process()
# print("Result 1:", vectors2[0]['text'])
# =============================================================================
# chatbot_pipeline.py
# Extracted from chatbot-pipeline-langgraph.ipynb
# Public API:
#   run_full_pipeline(query, metadata_filters, chat_history) -> dict
#   retrieve_only(query, k, filters) -> list[dict]
# =============================================================================

# ── Standard Library ──────────────────────────────────────────────────────────
import os
import sys
import re
import time
import json
import string
import ast
import logging
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Literal, Iterable, TypedDict, Optional, Any, Dict, List, Tuple, Callable
from collections import Counter

# ── Data & ML ─────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd

# ── LangChain Core ────────────────────────────────────────────────────────────
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

# ── LangChain Components ──────────────────────────────────────────────────────
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ── Retrieval ─────────────────────────────────────────────────────────────────
from rank_bm25 import BM25Okapi

# ── LangGraph ─────────────────────────────────────────────────────────────────
from langgraph.graph import StateGraph, START, END

# ── Environment ───────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(override=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
# All data files live in chatbot/files/ relative to this module
BASE_DIR = Path(__file__).parent / "files"
CHROMA_DIR = Path(__file__).parent / "chroma_db"

# ── Colored logging ───────────────────────────────────────────────────────────
if os.name == "nt":
    os.system("")  # enable ANSI escape codes on Windows 10+

_C = {
    "reset":   "\033[0m",
    "dim":     "\033[2m",
    "bold":    "\033[1m",
    "grey":    "\033[90m",
    "green":   "\033[92m",
    "red":     "\033[91m",
    "yellow":  "\033[93m",
    "blue":    "\033[94m",
    "cyan":    "\033[96m",
    "magenta": "\033[95m",
    "white":   "\033[97m",
}

_TAG_COLORS = {
    "[OK]":       _C["green"],
    "[ERR]":      _C["red"],
    "[WARN]":     _C["yellow"],
    "[FILTER]":   _C["cyan"],
    "[SEARCH]":   _C["blue"],
    "[ROUTE]":    _C["magenta"],
    "[EVAL]":     _C["blue"],
    "[LOAD]":     _C["cyan"],
    "[BUILD]":    _C["cyan"],
    "[DOCS]":     _C["white"],
    "[MSG]":      _C["white"],
    "[IN]":       _C["green"],
    "[LLM]":      _C["magenta"],
    "[GEN]":      _C["magenta"],
    "[PERSONA]":  _C["magenta"],
    "[INFO]":     _C["cyan"],
    "[STATS]":    _C["cyan"],
    "[CONTEXT]":  _C["cyan"],
    "[COMPRESS]": _C["grey"],
    "[SKIP]":     _C["grey"],
    "[SPLIT]":    _C["yellow"],
    "[BM25]":     _C["blue"],
    "[SEM]":      _C["blue"],
    "[HYB]":      _C["blue"],
    "[KW]":       _C["blue"],
    "[?]":        _C["grey"],
}

_USE_COLOR = sys.stdout.isatty()

class _ColorFormatter(logging.Formatter):
    _prefix_re = re.compile(r"\[(PIPELINE|ROUTER|RETRIEVAL|MESSENGER BOT|COMMENTS BOT)\]")
    _quote_re  = re.compile(r'"([^"\n]{1,150})"')
    _arrow_re  = re.compile(r"(>> Query:)")

    def format(self, record):
        msg = super().format(record)
        if not _USE_COLOR:
            return msg
        # Dim the module prefix  [PIPELINE], [ROUTER], etc.
        msg = self._prefix_re.sub(
            lambda m: f"{_C['grey']}[{m.group(1)}]{_C['reset']}", msg)
        # Color the tag tokens
        for tag, color in _TAG_COLORS.items():
            if tag in msg:
                msg = msg.replace(tag, f"{color}{tag}{_C['reset']}")
        # Bold-green the query-start marker
        msg = self._arrow_re.sub(
            lambda m: f"{_C['bold']}{_C['green']}{m.group(1)}{_C['reset']}", msg)
        # Bright-white the quoted previews ("…")
        msg = self._quote_re.sub(
            lambda m: f'{_C["white"]}"{m.group(1)}"{_C["reset"]}', msg)
        return msg

_logger = logging.getLogger("pipeline")
_logger.setLevel(logging.INFO)
_logger.propagate = False
if not _logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(_ColorFormatter("%(message)s"))
    _logger.addHandler(_h)

def _log(msg: str):
    _logger.info(msg)


# =============================================================================
# LLM FACTORY
# =============================================================================

@dataclass
class LLMConfig:
    provider: str
    model: str


def _build_llm(cfg: LLMConfig):
    """Factory: build LLM from config. Supports Groq, OpenAI, Ollama, HuggingFace, Google."""
    provider = (cfg.provider or "").lower().strip()

    if provider in {"google", "gemini"}:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=cfg.model, temperature=0.0)

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=cfg.model, temperature=0.0)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=cfg.model, temperature=0.0)

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=cfg.model, base_url=base_url, temperature=0.0)

    if provider in {"huggingface", "hf"}:
        from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        endpoint = HuggingFaceEndpoint(
            repo_id=cfg.model,
            task="text-generation",
            max_new_tokens=1024,
            temperature=0.2,
        )
        return ChatHuggingFace(llm=endpoint)

    return None


light_llm = _build_llm(LLMConfig(
    provider=os.environ.get("LIGHT_LLM_PROVIDER", ""),
    model=os.environ.get("LIGHT_LLM_MODEL", ""),
))
good_llm = _build_llm(LLMConfig(
    provider=os.environ.get("GOOD_LLM_PROVIDER", ""),
    model=os.environ.get("GOOD_LLM_MODEL", ""),
))
generation_llm = _build_llm(LLMConfig(
    provider=os.environ.get("GENERATION_LLM_PROVIDER", ""),
    model=os.environ.get("GENERATION_LLM_MODEL", ""),
)) or good_llm  # fallback to good_llm if generation LLM is not configured

_log(f"[PIPELINE] Light LLM:      {getattr(light_llm, 'model_name', None) or getattr(light_llm, 'model', 'not configured')}")
_log(f"[PIPELINE] Good LLM:       {getattr(good_llm, 'model_name', None) or getattr(good_llm, 'model', 'not configured')}")
_log(f"[PIPELINE] Generation LLM: {getattr(generation_llm, 'model_name', None) or getattr(generation_llm, 'model', 'not configured')}")


# =============================================================================
# QUERY COMPRESSION: Domain Vocabulary
# =============================================================================

def sanitize_text(text):
    """Remove punctuation and convert to lowercase."""
    return str(text).lower().translate(str.maketrans('', '', string.punctuation))


try:
    from nltk.stem import WordNetLemmatizer
    import nltk
    nltk.download('wordnet', quiet=True)
    _lemmatizer = WordNetLemmatizer()
    USE_NLTK = True
except ImportError:
    _lemmatizer = None
    USE_NLTK = False


def clean_token(token: str) -> str:
    """Normalize a single token: lowercase, strip, and lemmatize if NLTK is available."""
    token = str(token).strip().lower()
    if USE_NLTK and _lemmatizer and len(token) > 2:
        return _lemmatizer.lemmatize(token)
    return token


# =============================================================================
# COLUMN → VOCAB MAPPING  (single source of truth)
# Used by DomainVocabularyBuilder when writing vocab, and by
# route_2_product_query when reading vocab to build filters.
# =============================================================================
COLUMN_TO_VOCAB: Dict[str, str] = {
    "Gender":      "gender",
    "Colour":      "colors",   "Color":    "colors",
    "BrandName":   "brands",   "Brand":    "brands",
    "Category":    "categories",
    "SubCategory": "subcategories",
    "ProductType": "products",
    "Size":        "sizes",
    "Usage":       "styles",   "Style":    "styles",
    "Material":    "materials",
}


class DomainVocabularyBuilder:
    """The Best of Both Worlds: Robust, Optimized, Smart Domain Extraction."""

    def __init__(self, fashion_df):
        self.fashion_df = fashion_df
        self.vocabulary = {
            'brands': set(), 'colors': set(),
            'categories': set(), 'subcategories': set(), 'products': set(),
            'materials': set(), 'sizes': set(), 'styles': set(),
            'gender': set(), 'all_tokens': set()
        }

    def _clean_token(self, token):
        return clean_token(token)

    def extract_from_structured_columns(self):
        """Extracts structured column values into vocab buckets using COLUMN_TO_VOCAB."""
        print("\n[1] Extracting from structured columns...")

        for col in self.fashion_df.columns:
            # Exact match first (preferred), then case-insensitive substring fallback
            vocab_key = COLUMN_TO_VOCAB.get(col)
            if vocab_key is None:
                col_lower = col.lower()
                for key, vk in COLUMN_TO_VOCAB.items():
                    if key.lower() in col_lower:
                        vocab_key = vk
                        break
            # Brands are handled by extract_brands(); skip here to avoid duplication
            if not vocab_key or vocab_key == 'brands':
                continue
            tokens = {
                self._clean_token(t) for val in self.fashion_df[col].dropna()
                for t in str(val).split(',') if len(str(t).strip()) > 1
            }
            if tokens:
                self.vocabulary[vocab_key].update(tokens)
                print(f"  + Extracted {len(tokens)} {vocab_key} from column '{col}'")

    def extract_brands(self):
        """Specific dynamic extraction for Brand columns."""
        print("\n[2] Mining for specific brand columns...")
        brand_cols = [c for c in self.fashion_df.columns if 'brand' in str(c).lower()]
        for col in brand_cols:
            brands = {str(b).strip().lower() for b in self.fashion_df[col].dropna() if len(str(b).strip()) > 1}
            self.vocabulary['brands'].update(brands)
            print(f"  + Extracted {len(brands)} brands from '{col}'")

    def extract_products_from_titles(self):
        """Advanced logic to find missing products focusing on head nouns and excluding knowns."""
        print("\n[3] Mining titles for additional product nouns...")

        cats_to_exclude = ['brands', 'colors', 'gender', 'styles', 'materials', 'categories', 'subcategories']
        exclusions = set().union(*(self.vocabulary[cat] for cat in cats_to_exclude))
        noise = {'navy', 'golden', 'length', 'lifestyle', 'coloured', 'kids', 'men', 'women', 'canvas', 'leather', 'printed'}

        word_pattern = re.compile(r'\b\w+\b')
        potential_products = []

        for title in self.fashion_df['ProductTitle'].dropna():
            words = word_pattern.findall(str(title).lower())
            if not words: continue

            candidates = [words[-1]]
            if len(words) > 1:
                candidates.append(words[-2])

            for word in candidates:
                word_clean = self._clean_token(word)
                if len(word_clean) > 2 and word_clean not in exclusions and word_clean not in noise and not word_clean.isnumeric():
                    potential_products.append(word_clean)

        word_counts = Counter(potential_products)
        common_nouns = {word for word, count in word_counts.items() if count >= 3}

        self.vocabulary['products'].update(common_nouns)
        print(f"  + Added {len(common_nouns)} highly-probable product types from titles.")

    def inject_hardcoded_failsafe(self):
        """Ensure crucial baseline descriptors always exist, protecting against partial data or LLM failure."""
        print("\n[4] Injecting baseline failsafe descriptors...")
        gender_terms = {'men', 'mens', "men's", 'women', 'womens', "women's", 'unisex',
                        'boys', 'boy', "boy's", 'girls', 'girl', "girl's", 'kids', "kids'",
                        'infant', 'baby', 'toddler', 'children', 'kidswear', 'son', 'daughter'}
        self.vocabulary['gender'].update(self._clean_token(t) for t in gender_terms)
        print(f"  + Injected {len(gender_terms)} core routing terms for gender.")

    def add_llm_descriptors(self, genai_client=None):
        """Dynamic domain review and expansion via Google GenAI SDK, strictly enforcing JSON format."""
        if not genai_client:
            print("\n[5] Skipping LLM augmentation: no LLM client provided.")
            return

        print("\n[5] Calling Gemini LLM for domain sanitization and expansion (Strict JSON mode)...")

        # Excluded brands entirely to protect raw CSV data
        current_state = {
            'gender': list(self.vocabulary['gender']),
            'colors': list(self.vocabulary['colors']),
            'styles': list(self.vocabulary['styles']),
            'materials': list(self.vocabulary['materials']),
            'products': list(self.vocabulary['products'])
        }
        state_json = json.dumps(current_state, indent=2)

        prompt = f"""You are an elite Fashion Domain Data Scientist.
I am providing you with a raw, extracted fashion dataset vocabulary in JSON format. It contains noisy and irrelevant terms, and is likely missing key generic fashion terms.

Your tasks:
1. REVIEW AND CLEAN: Prune each category. Remove words that are pure numbers, nonsensical, misspellings, or definitively NOT related to fashion clothing. For colors, products, materials, and styles, be strictly rigorous and permanently remove noise like 'printed', 'lifestyle', 'length', 'toprated', etc.
2. EXPAND: Add any fundamental fashion descriptors that are completely missing from each category to make it a globally comprehensive dictionary.

Return ONLY a valid JSON object strictly matching these 5 exact keys: 'gender', 'styles', 'materials', 'colors', 'products', each containing arrays of cleaned, lowercase python strings.

Here is the current raw vocabulary state limit output to json:
{state_json}"""

        try:
            from google.genai import types

            response = genai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                    max_output_tokens=8192
                )
            )
            llm_vocab = json.loads(response.text)

            target_keys = ['gender', 'colors', 'styles', 'materials', 'products']
            print("  + Received LLM Review...")

            for category in target_keys:
                if category in llm_vocab and isinstance(llm_vocab[category], list):
                    original_len = len(self.vocabulary[category])
                    clean_terms = {self._clean_token(t) for t in llm_vocab[category] if len(str(t).strip()) > 1}
                    self.vocabulary[category] = clean_terms
                    new_len = len(clean_terms)
                    diff = new_len - original_len
                    sign = "+" if diff >= 0 else ""
                    print(f"    - {category.capitalize()}: {original_len} -> {new_len} terms ({sign}{diff})")

        except Exception as e:
            print(f"  [WARN] LLM domain review/expansion failed: {e}. Relying solely on CSV data.")

    def build_and_save(self, genai_client=None, filename="domain_vocabulary.json"):
        """Execute the full pipeline, flatten, and export the vocabulary."""
        print("\n" + "*"*50)
        print("BUILDING MIXED DOMAIN VOCABULARY")
        print("*"*50)

        self.extract_from_structured_columns()
        self.extract_brands()
        self.extract_products_from_titles()
        self.inject_hardcoded_failsafe()
        self.add_llm_descriptors(genai_client)

        # Consolidate 'all_tokens' for your router into purely lowercase generic terms
        for cat, terms in self.vocabulary.items():
            if cat != 'all_tokens':
                self.vocabulary['all_tokens'].update({str(t).strip().lower() for t in terms})

        # Convert sets to sorted lists for clean JSON rendering
        final_vocab = {k: sorted(list(v)) for k, v in self.vocabulary.items()}

        print("\n[STATS] Final Domain Vocabulary Summary")
        for category, tokens in final_vocab.items():
            if category != 'all_tokens' and tokens:
                print(f"  {category:15s}: {len(tokens):4d} terms")
        print(f"\n+ TOTAL UNIQUE TOKENS (all_tokens): {len(final_vocab['all_tokens'])}")

        try:
            dir_name = os.path.dirname(filename)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_vocab, f, indent=4, ensure_ascii=False)
            print(f"\n[OK] Domain explicitly saved to '{filename}' for router.")
        except Exception as e:
            print(f"\n[WARN] Failed to export '{filename}': {e}")

        # Update metadata_schema.json with actual unique values per filterable column
        self._save_metadata_schema(filename)

        return final_vocab

    def _save_metadata_schema(self, vocab_filename: str):
        """Overwrite metadata_schema.json as a dict: field → sorted unique actual values.
        Lets route_2_product_query resolve vocab terms to real metadata values at query time."""
        try:
            schema_path = Path(vocab_filename).parent / "metadata_schema.json"
            primary_cols = {col for col in COLUMN_TO_VOCAB if col in self.fashion_df.columns}
            metadata_schema = {
                col: sorted(
                    self.fashion_df[col].dropna().astype(str).str.strip().unique().tolist()
                )
                for col in primary_cols
            }
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_schema, f, indent=4, ensure_ascii=False)
            print(f"[OK] Metadata schema (with actual values) saved to '{schema_path}'.")
        except Exception as e:
            print(f"[WARN] Failed to export metadata schema: {e}")


def smart_compress_query(query, domain_vocab):
    """Compress query by extracting only domain-relevant tokens."""
    query = str(query).lower()
    greetings = r'^(hey|hi|hello|greetings)(\s+there)?\s+'
    conversational = [
        r'\b(i\s+)?am\s+looking\s+for\b', r'\blooking\s+for\b',
        r'\bdo\s+you\s+have\s+(any\s+)?\b', r'\bcan\s+you\s+show\s+(me\s+)?\b',
        r'\b(show\s+me|i\s+(want|need)|please|thanks?|thank\s+you)\b'
    ]
    query = re.sub(greetings, '', query)
    for pattern in conversational:
        query = re.sub(pattern, ' ', query)
    query = sanitize_text(query)
    tokens = query.split()

    relevant_tokens = []
    structural_words = {'in', 'and', 'or', 'size', 'color', 'type'}
    possessive_words = {'my', 'your', 'his', 'her', 'their', 'our'}
    gender_terms = set(domain_vocab.get('gender', []))
    all_tokens = domain_vocab.get('all_tokens', [])
    all_tokens = set(str(t).lower().strip() for t in all_tokens if str(t).strip())

    for i, token in enumerate(tokens):
        raw = token.strip()
        normalized = clean_token(raw)
        if normalized in all_tokens:
            relevant_tokens.append(raw)
        elif raw in possessive_words:
            next_token = tokens[i + 1].strip() if i + 1 < len(tokens) else ''
            if next_token in gender_terms:
                relevant_tokens.append(raw)
        elif raw in structural_words and relevant_tokens:
            relevant_tokens.append(raw)
        elif raw.isdigit():
            relevant_tokens.append(raw)

    compressed = ' '.join(relevant_tokens)
    return re.sub(r'\s+', ' ', compressed).strip()


# =============================================================================
# ADAPTIVE RAG ROUTING
# =============================================================================

class QueryRoute(Enum):
    IRRELEVANT = 0
    COMPANY_RELATED = 1
    PRODUCT_QUERY = 2


def load_routing_config():
    """Load configuration files needed for routing."""
    config = {'company_info': {}, 'irrelevant_template': '', 'greeting_template': '', 'domain_vocab': {}}

    try:
        with open(BASE_DIR / "company_info.json", encoding="utf-8-sig") as f:
            config['company_info'] = json.load(f)
    except FileNotFoundError:
        _log("[PIPELINE] [WARN] company_info.json not found")

    try:
        with open(BASE_DIR / "company_irrelevant_template_reply.json", encoding="utf-8-sig") as f:
            irrelevant_data = json.load(f)
            config['irrelevant_template'] = (
                irrelevant_data.get("company_data", {})
                .get("fallback_response", {})
                .get("value", "")
            )
    except FileNotFoundError:
        _log("[PIPELINE] [WARN] company_irrelevant_template_reply.json not found")

    try:
        with open(BASE_DIR / "company_greeting_template_reply.json", encoding="utf-8-sig") as f:
            greeting_data = json.load(f)
            config['greeting_template'] = (
                greeting_data.get("company_data", {})
                .get("greeting_response", {})
                .get("value", "")
            )
    except FileNotFoundError:
        _log("[PIPELINE] [WARN] company_greeting_template_reply.json not found")

    try:
        with open(BASE_DIR / "domain_vocabulary.json", encoding="utf-8-sig") as f:
            config['domain_vocab'] = json.load(f)
        if 'all_tokens' not in config['domain_vocab']:
            all_tokens = set()
            for category, terms in config['domain_vocab'].items():
                if isinstance(terms, list):
                    all_tokens.update(str(t).lower().strip() for t in terms if str(t).strip())
            config['domain_vocab']['all_tokens'] = sorted(all_tokens)
    except FileNotFoundError:
        _log("[PIPELINE] [WARN] domain_vocabulary.json not found")

    return config


routing_config = load_routing_config()


def extract_company_keywords(company_info: dict) -> list:
    keywords = set()
    company_data = company_info.get("company_data", {})
    for key, metadata in company_data.items():
        keywords.update(key.split('_'))
        if "key" in metadata:
            keywords.add(metadata["key"].lower())
        if "description" in metadata:
            desc_words = metadata["description"].lower().split()
            relevant_words = [w.strip('.,') for w in desc_words if len(w) > 3]
            keywords.update(relevant_words[:5])
    keywords.update([
        "company", "contact", "location", "founder", "about",
        "phone", "email", "store", "address", "hours",
        "opening", "closing", "customer", "care", "support",
        "office", "branch", "headquarter", "team"
    ])
    return sorted(list(keywords))


def extract_product_keywords(domain_vocab: dict) -> list:
    keywords = set()
    for category, terms in domain_vocab.items():
        if isinstance(terms, list):
            keywords.update(term.lower() for term in terms)
    keywords.update(["product", "buy", "sell", "price", "purchase", "shop", "shopping"])
    return sorted(list(keywords))


COMPANY_KEYWORDS = extract_company_keywords(routing_config['company_info'])
PRODUCT_KEYWORDS = extract_product_keywords(routing_config['domain_vocab'])


def detect_query_complexity(user_query: str) -> Tuple[bool, int]:
    query_lower = user_query.lower()
    complexity_indicators = [r'and|or|also|as well as|additionally|plus', r'\?.*\?']
    complexity_score = sum(1 for pattern in complexity_indicators if re.search(pattern, query_lower))
    return complexity_score > 0, complexity_score


def split_query(user_query: str) -> List[str]:
    is_complex, _ = detect_query_complexity(user_query)
    if not is_complex:
        return [user_query.strip()]
    split_pattern = r"\b(?:and|also|plus|as well as|additionally)\b|\?+"
    parts = [part.strip(" ?") for part in re.split(split_pattern, user_query) if part.strip(" ?")]
    return parts if parts else [user_query.strip()]


_GREETING_RE = re.compile(
    r"^(hi|hey|hello|hiya|howdy|greetings|"
    r"good\s+(morning|afternoon|evening|day)|"
    r"how\s+are\s+you|what'?s\s+up|sup|yo|"
    # Arabic
    r"salaam|salam|مرحبا|أهلا|أهلاً|السلام\s+عليكم|"
    # French
    r"bonjour|bonsoir|salut|"
    # Spanish / Portuguese
    r"hola|ola|"
    # Italian / Turkish / German / other
    r"ciao|merhaba|hallo|guten\s+(morgen|tag|abend)|namaste"
    r")\W*$",
    re.IGNORECASE,
)


def determine_route(query: str) -> QueryRoute:
    query_lower = query.lower()
    company_score = sum(1 for kw in COMPANY_KEYWORDS if kw in query_lower)
    product_score = sum(1 for kw in PRODUCT_KEYWORDS if kw in query_lower)
    if company_score > 0 and product_score == 0:
        return QueryRoute.COMPANY_RELATED
    elif product_score > 0 and company_score == 0:
        return QueryRoute.PRODUCT_QUERY
    elif company_score > 0 and product_score > 0:
        return QueryRoute.PRODUCT_QUERY
    else:
        return QueryRoute.IRRELEVANT


def route_0_irrelevant_query(query: str, username: str = "") -> Dict[str, Any]:
    template = routing_config.get(
        'irrelevant_template',
        "Sorry {{username}}, I cannot help with that. At Fashion Hub, we specialize in fashion products."
    )
    if username:
        response_text = template.replace("{{username}}", username)
    else:
        # Strip "{{username}}, " or "{{username}} " so no orphaned comma appears
        response_text = re.sub(r'\{\{username\}\},?\s*', '', template)
    return {"query": query, "route": QueryRoute.IRRELEVANT.name, "route_value": 0, "response": response_text}


def route_1_company_query(query: str) -> Dict[str, Any]:
    company_data = routing_config['company_info'].get("company_data", {})
    # Lemmatize query tokens so "location" matches "locations", "address" matches "addresses", etc.
    query_tokens = {clean_token(w) for w in query.lower().split()}
    matched_metadata = {}
    for key, metadata in company_data.items():
        key_text = metadata.get("key", "").lower()
        description = metadata.get("description", "").lower()
        key_words = {clean_token(w) for w in key.split('_')}
        key_text_words = {clean_token(w) for w in key_text.split()}
        desc_words = {clean_token(w) for w in description.split()[:5]}
        if key_words & query_tokens or key_text_words & query_tokens or desc_words & query_tokens:
            matched_metadata[key] = metadata.get("value", "")
    if not matched_metadata:
        matched_metadata = {k: v.get("value", "") for k, v in company_data.items()}
    return {"query": query, "route": QueryRoute.COMPANY_RELATED.name, "route_value": 1, "company_response": matched_metadata}


def route_2_product_query(query: str, compressed_query: str = None) -> Dict[str, Any]:
    query_for_filtering = (compressed_query or query or "").lower()

    # Load metadata schema: dict format (field → actual unique values) preferred;
    # falls back to legacy flat-list (no actual values) if not yet regenerated.
    metadata_schema_values: Dict[str, List[str]] = {}
    try:
        with open(BASE_DIR / "metadata_schema.json", "r", encoding="utf-8-sig") as f:
            loaded_schema = json.load(f)
            if isinstance(loaded_schema, dict):
                metadata_schema_values = loaded_schema
            elif isinstance(loaded_schema, list):
                metadata_schema_values = {col: [] for col in loaded_schema if col != "ProductId"}
    except FileNotFoundError:
        metadata_schema_values = {k: [] for k in ["Gender", "Category", "SubCategory", "ProductType", "Colour", "BrandName", "Size", "Usage"]}

    domain_vocab = {}
    try:
        with open(BASE_DIR / "domain_vocabulary.json", "r", encoding="utf-8-sig") as f:
            loaded_vocab = json.load(f)
            if isinstance(loaded_vocab, dict):
                domain_vocab = loaded_vocab
    except FileNotFoundError:
        domain_vocab = routing_config.get('domain_vocab', {}) or {}

    # Pre-compute lemmatized query tokens once for all fields
    _query_lemma_tokens = {clean_token(t) for t in query_for_filtering.split() if t.strip()}

    filters: Dict[str, List[str]] = {}
    for schema_field, actual_values in metadata_schema_values.items():
        vocab_key = COLUMN_TO_VOCAB.get(schema_field)
        if not vocab_key:
            continue
        terms = domain_vocab.get(vocab_key, [])
        if not isinstance(terms, list):
            continue
        # Find vocab terms present in the query.
        # Two-pass: (1) exact whole-word regex (handles multi-word terms like "flip flops"),
        # (2) lemma-token match to handle plural/inflected forms ("socks" → "sock").
        matched_terms = {
            clean_token(term) for term in terms
            if str(term).strip() and (
                re.search(
                    r"\b" + re.escape(str(term).strip().lower()) + r"\b",
                    query_for_filtering
                )
                or clean_token(str(term).strip()) in _query_lemma_tokens
            )
        }
        if not matched_terms:
            continue
        if actual_values:
            # Resolve vocab terms → real metadata values via fuzzy matching
            matched_actual = sorted({
                v for v in actual_values
                for t in matched_terms
                if _term_matches_value(t, clean_token(v))
            })
            if matched_actual:
                filters[schema_field] = matched_actual
        else:
            # Fallback: no actual values available, use vocab terms directly
            filters[schema_field] = sorted(matched_terms)

    if filters:
        _log(f"[ROUTER] [FILTER] Metadata filters built: {filters}")
    else:
        _log("[ROUTER] [FILTER] No metadata filters matched — unfiltered retrieval")
    return {"query": query, "compressed_query": compressed_query, "route": QueryRoute.PRODUCT_QUERY.name,
            "route_value": 2, "metadata_filters": filters}


# =============================================================================
# LANGGRAPH ROUTING GRAPH
# =============================================================================

class RouterState(TypedDict):
    original_query: str
    query: str
    compressed_query: Optional[str]
    route: Optional[QueryRoute]
    username: Optional[str]
    response: Optional[Dict[str, Any]]
    company_response: Optional[Dict]
    metadata_filters: Optional[Dict]


def decision_node(state: RouterState) -> RouterState:
    query = state["query"]
    route = determine_route(query)
    compressed = smart_compress_query(query, routing_config['domain_vocab'])
    state["route"] = route
    state["compressed_query"] = compressed
    return state


def route_0_node(state: RouterState) -> RouterState:
    query = state["query"]
    username = state.get("username") or ""
    response = route_0_irrelevant_query(query, username)
    state["response"] = response.get("response")
    return state


def route_1_node(state: RouterState) -> RouterState:
    query = state["query"]
    response = route_1_company_query(query)
    state["company_response"] = response.get("company_response", {})
    return state


def route_2_node(state: RouterState) -> RouterState:
    query = state["query"]
    compressed = state.get("compressed_query", query)
    response = route_2_product_query(query, compressed)
    state["metadata_filters"] = response.get("metadata_filters", {})
    state["compressed_query"] = response.get("compressed_query", query)
    return state


def create_routing_graph() -> Any:
    workflow = StateGraph(RouterState)
    workflow.add_node("decision", decision_node)
    workflow.add_node("route_0", route_0_node)
    workflow.add_node("route_1", route_1_node)
    workflow.add_node("route_2", route_2_node)
    workflow.set_entry_point("decision")

    def _route_decision(state: RouterState) -> Literal["route_0", "route_1", "route_2"]:
        route = state.get("route")
        if route == QueryRoute.IRRELEVANT:
            return "route_0"
        elif route == QueryRoute.COMPANY_RELATED:
            return "route_1"
        return "route_2"

    workflow.add_conditional_edges("decision", _route_decision,
                                   {"route_0": "route_0", "route_1": "route_1", "route_2": "route_2"})
    workflow.add_edge("route_0", END)
    workflow.add_edge("route_1", END)
    workflow.add_edge("route_2", END)
    return workflow.compile()


routing_graph = create_routing_graph()


# =============================================================================
# DATA PREPROCESSING: UniversalRAGIngestor
# =============================================================================

class UniversalRAGIngestor:
    def __init__(self, df, name_col, desc_col=None, llm=None, schema_file=None):
        self.df = df
        self.name_col = name_col
        self.desc_col = desc_col
        self.llm = llm
        self.schema_file = schema_file or str(BASE_DIR / "metadata_schema.json")
        if self.llm is None:
            _log("[PIPELINE] [WARN] No LLM configured for ingestor; using fallback logic.")

    def _call_agent_for_metadata_selection(self, sample_data):
        if self.llm is None:
            exclude = [self.name_col, self.desc_col] if self.desc_col else [self.name_col]
            return [c for c in self.df.columns if c not in exclude]
        prompt = f"""You are a Data Engineer.\nHere is a sample of dataset columns and values:\n{json.dumps(sample_data)}\n
Task: Identify which columns represents useful "Metadata" (facets, categories, tags, pricing, grouping).\nRules:\n1. INCLUDE unique IDs (like 'ProductId', 'UUID').\n2. EXCLUDE URLs or Image links.\n3. EXCLUDE the primary name column: '{self.name_col}'.\n4. INCLUDE categorical fields (Gender, Color, Cuisine) or metrics (Price, Rating).\n5. Return ONLY a valid Python list of strings. No markdown, no explanation.\nExample Output: ['Color', 'Size', 'Brand']"""
        messages = [
            SystemMessage(content="You extract metadata schema from data. Output only a Python list."),
            HumanMessage(content=prompt)
        ]
        try:
            result = self.llm.invoke(messages)
            clean_text = result.content.strip().replace("```python", "").replace("```", "").strip()
            if "[" in clean_text:
                start = clean_text.find("[")
                end = clean_text.rfind("]") + 1
                clean_text = clean_text[start:end]
            selected_cols = ast.literal_eval(clean_text)
            return [c for c in selected_cols if c in self.df.columns]
        except Exception as e:
            _log(f"[PIPELINE] [WARN] Metadata agent failed: {e}. Using all columns.")
            exclude = [self.name_col, self.desc_col] if self.desc_col else [self.name_col]
            return [c for c in self.df.columns if c not in exclude]

    def _call_agent_for_template(self, sample_data):
        if self.llm is None:
            return f"{{ {self.name_col} }}"
        prompt = f"""Data Sample: {json.dumps(sample_data)}\nTask: Create a natural language sentence template to describe this data item.\nUse Python .format() notation (curly braces) for column names.\nReturn ONLY the template string."""
        messages = [
            SystemMessage(content="You are a data processing engine. Output raw text templates only."),
            HumanMessage(content=prompt)
        ]
        try:
            result = self.llm.invoke(messages)
            clean_text = result.content.strip().replace("```", "").strip()
            if (clean_text.startswith('"') and clean_text.endswith('"')):
                clean_text = clean_text[1:-1]
            return clean_text
        except Exception:
            return f"{{ {self.name_col} }}"

    def process(self):
        sample = self.df.head(3).to_dict(orient='records')
        _log("[PIPELINE] [LLM] Analyzing columns for importance...")
        self.meta_cols = self._call_agent_for_metadata_selection(sample)
        _log(f"[PIPELINE] [OK] Metadata columns: {self.meta_cols}")
        try:
            with open(self.schema_file, 'w', encoding='utf-8') as f:
                json.dump(self.meta_cols, f, indent=4)
        except Exception as e:
            _log(f"[PIPELINE] [WARN] Could not save metadata schema: {e}")

        if self.desc_col and self.desc_col in self.df.columns:
            template = None
        else:
            _log("[PIPELINE] [LLM] Generating description template...")
            template = self._call_agent_for_template(sample)
            _log(f"[PIPELINE] [OK] Template: \"{template}\"")

        non_meta_cols = [c for c in self.df.columns if c not in self.meta_cols]
        results = []
        for idx, row in self.df.iterrows():
            metadata = {col: row[col] for col in self.meta_cols if pd.notna(row[col])}
            non_meta_dict = {col: row[col] for col in non_meta_cols if pd.notna(row[col])}
            if non_meta_dict:
                metadata["additional_data"] = json.dumps(non_meta_dict, default=str)
            if "ProductId" in self.df.columns:
                metadata["ProductId"] = str(int(row["ProductId"]))
            if template:
                try:
                    text_to_embed = template.format(**row.to_dict())
                except KeyError:
                    text_to_embed = f"{row[self.name_col]}"
            else:
                text_to_embed = f"{row[self.name_col]}. {row[self.desc_col]}"
            results.append({"id": str(idx), "text": text_to_embed, "metadata": metadata})
        return results


# =============================================================================
# DATA LOADING & INDEXING
# =============================================================================

EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
embedding_function = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)


def store_in_vector_database(data_results: list) -> list:
    docs = []
    for record in data_results:
        doc = Document(page_content=record['text'], metadata=record['metadata'], id=record['id'])
        docs.append(doc)
    return docs


def index_documents(docs: list, persist_directory: str = None, collection_name: str = "product_catalog"):
    persist_directory = persist_directory or str(CHROMA_DIR)
    vector_store = Chroma.from_documents(
        documents=docs, embedding=embedding_function,
        persist_directory=persist_directory, collection_name=collection_name
    )
    _log(f"[PIPELINE] [OK] Indexed {len(docs)} documents to {persist_directory}")
    return vector_store


def load_vector_database(persist_directory: str = None, collection_name: str = "product_catalog"):
    persist_directory = persist_directory or str(CHROMA_DIR)
    return Chroma(persist_directory=persist_directory, embedding_function=embedding_function,
                  collection_name=collection_name)


def preprocess_for_bm25(text: str) -> list:
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    tokens = text.split()
    return [t for t in tokens if t and len(t) > 1]


# ── Data Pipeline: Load or Create ─────────────────────────────────────────────

_CSV_PATH = Path(os.environ.get("CSV_PATH", str(BASE_DIR / "fashion.csv")))
_CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", str(CHROMA_DIR))
_COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "product_catalog")
_FORCE_REINDEX = os.environ.get("FORCE_REINDEX", "false").lower() == "true"

_chroma_exists = Path(_CHROMA_PERSIST_DIR).exists() and any(Path(_CHROMA_PERSIST_DIR).iterdir())

if _chroma_exists and not _FORCE_REINDEX:
    _log("[PIPELINE] [LOAD] Loading vector store from ChromaDB")
    vector_store = load_vector_database(persist_directory=_CHROMA_PERSIST_DIR, collection_name=_COLLECTION_NAME)
    _raw = vector_store.get()
    _doc_count = len(_raw.get('ids', []))
    _log(f"[PIPELINE] [OK] Vector store loaded ({_doc_count} documents)")
    langchain_docs = [
        Document(page_content=_raw['documents'][i],
                 metadata=_raw['metadatas'][i] if _raw['metadatas'] else {},
                 id=_raw['ids'][i])
        for i in range(_doc_count)
    ]
else:
    _log("[PIPELINE] [LOAD] Processing data from CSV")
    _df = pd.read_csv(_CSV_PATH, encoding="utf-8")
    _log(f"[PIPELINE] [OK] Loaded {len(_df)} rows from CSV")
    _NAME_COL = os.environ.get("NAME_COL", "ProductTitle")
    _DESC_COL = os.environ.get("DESC_COL", None)
    _log("[PIPELINE] [LLM] Processing with UniversalRAGIngestor...")
    _ingestor = UniversalRAGIngestor(df=_df, name_col=_NAME_COL, desc_col=_DESC_COL, llm=good_llm)
    _data_results = _ingestor.process()
    _log(f"[PIPELINE] [OK] Processed {len(_data_results)} records")
    langchain_docs = store_in_vector_database(_data_results)
    _log("[PIPELINE] [BUILD] Indexing in ChromaDB")
    vector_store = index_documents(docs=langchain_docs, persist_directory=_CHROMA_PERSIST_DIR,
                                   collection_name=_COLLECTION_NAME)

_log("[PIPELINE] [BUILD] Building BM25 index...")
_corpus_tokens = [preprocess_for_bm25(doc.page_content) for doc in langchain_docs]
bm25 = BM25Okapi(_corpus_tokens)
_log(f"[PIPELINE] [OK] BM25 ready ({len(langchain_docs)} documents)")
embeddings = embedding_function  # alias


# =============================================================================
# SEARCH FUNCTIONS (Hybrid Retrieval)
# =============================================================================

def _term_matches_value(term: str, value_norm: str) -> bool:
    """Check whether a normalized vocab term corresponds to a normalized metadata value.
    Handles compound words (e.g. 'top' → 'topwear', 'shirt' → 'tshirt')."""
    if value_norm == term:
        return True
    if value_norm.startswith(term) or value_norm.endswith(term):
        return True
    if len(term) >= 4 and term in value_norm:
        return True
    return False


def _passes_metadata_filter(metadata: dict, filters: dict | None) -> bool:
    if not filters:
        return True

    def _norm(value) -> str:
        if value is None:
            return ""
        return str(value).strip().lower()

    for key, value in filters.items():
        if value is None or value == "" or value == []:
            continue
        doc_value = metadata.get(key)
        if isinstance(value, (list, tuple, set)):
            allowed_values = {_norm(v) for v in value if v is not None and _norm(v) != ""}
            if not allowed_values:
                continue
            if isinstance(doc_value, (list, tuple, set)):
                doc_values = {_norm(v) for v in doc_value if v is not None and _norm(v) != ""}
                if not (doc_values & allowed_values):
                    return False
            else:
                if _norm(doc_value) not in allowed_values:
                    return False
            continue
        target_value = _norm(value)
        if isinstance(doc_value, (list, tuple, set)):
            doc_values = {_norm(v) for v in doc_value if v is not None and _norm(v) != ""}
            if target_value not in doc_values:
                return False
        else:
            if _norm(doc_value) != target_value:
                return False
    return True


def bm25_search(query: str, k: int = 10, filters: dict | None = None) -> list:
    tokens = preprocess_for_bm25(query)
    if not tokens:
        return []
    scores = bm25.get_scores(tokens)
    scored = []
    filtered_out = 0
    for idx, score in enumerate(scores):
        doc = langchain_docs[idx]
        if not _passes_metadata_filter(doc.metadata, filters):
            filtered_out += 1
            continue
        scored.append({"id": idx, "text": doc.page_content, "metadata": doc.metadata,
                        "score": float(score), "source": "bm25"})
    scored.sort(key=lambda x: x["score"], reverse=True)
    if filters and filtered_out:
        _log(f"[RETRIEVAL] [FILTER] {filtered_out}/{len(langchain_docs)} docs excluded by filter")
    return scored[:k]


def semantic_search(query: str, k: int = 10, filters: dict | None = None) -> list:
    search_k = k * 5 if filters else k
    results_with_scores = vector_store.similarity_search_with_score(query, k=search_k)
    results = []
    for doc, score in results_with_scores:
        metadata = doc.metadata
        if not _passes_metadata_filter(metadata, filters):
            continue
        results.append({"id": metadata.get("ProductId", ""), "text": doc.page_content,
                         "metadata": metadata, "score": float(score), "source": "semantic"})
        if len(results) >= k:
            break
    return results


def _rrf_fuse(result_lists: Iterable[list], k: int = 10, rrf_k: int = 60) -> list:
    fused = {}
    for results in result_lists:
        for rank, item in enumerate(results, start=1):
            doc_id = item["id"]
            fused.setdefault(doc_id, {**item, "rrf_score": 0.0})
            fused[doc_id]["rrf_score"] += 1.0 / (rrf_k + rank)
    merged = list(fused.values())
    merged.sort(key=lambda x: x["rrf_score"], reverse=True)
    return merged[:k]


def hybrid_retrieve(query: str, k: int = 10, filters: dict | None = None) -> list:
    bm25_results = bm25_search(query, k=k, filters=filters)
    semantic_results = semantic_search(query, k=k, filters=filters)
    return _rrf_fuse([bm25_results, semantic_results], k=k)


def rerank_cross_encoder(query: str, docs: list, enabled: bool = False):
    if not enabled or not docs:
        return docs
    try:
        from sentence_transformers import CrossEncoder
    except Exception:
        return docs
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    pairs = [[query, d["text"]] for d in docs]
    if not pairs:
        return docs
    scores = reranker.predict(pairs)
    for i, s in enumerate(scores):
        docs[i]["rerank_score"] = float(s)
    docs.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
    return docs


# =============================================================================
# QUERY ROUTER (Adaptive Strategy Selection)
# =============================================================================

USE_LLM_CLASSIFIER = True
CLASSIFIER_LLM = light_llm


def classify_query_with_llm(query: str, llm=None) -> Literal["keyword", "semantic", "hybrid"]:
    if llm is None:
        return _classify_query_rules(query)
    prompt = f"""You are a query classifier for a product search system. Classify this query into ONE category:

KEYWORD: Use when query has specific product names, brands, colors, sizes, or structured attributes.
Examples: "Nike black shoes size 10", "women's red dress", "ADIDAS sandals for men"

SEMANTIC: Use when query describes intent, occasion, style, or asks for recommendations.
Examples: "something comfortable for summer", "outfit for a job interview"

HYBRID: Use when query mixes specific attributes WITH descriptive intent.
Examples: "elegant red dress for wedding", "comfortable Nike shoes for gym"

Query: "{query}"

Respond with exactly one word: keyword, semantic, or hybrid"""
    try:
        response = llm.invoke(prompt)
        result = response.content.strip().lower().split()[0]
        result = re.sub(r'[^a-z]', '', result)
        if result in ["keyword", "semantic", "hybrid"]:
            return result
        return _classify_query_rules(query)
    except Exception as e:
        _log(f"[PIPELINE] [WARN] LLM classification failed: {str(e)[:50]}. Using rules.")
        return _classify_query_rules(query)


def _classify_query_rules(query: str) -> Literal["keyword", "semantic", "hybrid"]:
    query_lower = query.lower().strip()
    words = query_lower.split()
    keyword_signals = 0
    semantic_signals = 0

    if re.search(r'\b\d{4,}\b', query):
        keyword_signals += 3
    if len(words) <= 3:
        keyword_signals += 1

    colors = ['red', 'blue', 'green', 'black', 'white', 'pink', 'yellow', 'purple', 'grey', 'brown']
    products = ['shirt', 'shoes', 'dress', 'pants', 'jeans', 'top', 'jacket', 'sandals', 'sneakers']
    brands = ['nike', 'adidas', 'puma', 'reebok', 'fila', 'clarks', 'gini and jony']

    has_color = any(c in query_lower for c in colors)
    has_product = any(p in query_lower for p in products)
    has_brand = any(b in query_lower for b in brands)

    if has_color and has_product:
        keyword_signals += 2
    if has_brand:
        keyword_signals += 2
    if any(query_lower.startswith(w) for w in ['do you have', 'is there', 'got any']):
        keyword_signals += 1

    semantic_phrases = ['something for', 'recommend', 'suggest', 'goes with', 'comfy', 'occasion']
    for phrase in semantic_phrases:
        if phrase in query_lower:
            semantic_signals += 2
    if any(query_lower.startswith(w) for w in ['what should', 'what would', 'how do i style']):
        semantic_signals += 2
    if len(words) >= 6:
        semantic_signals += 1

    total = keyword_signals + semantic_signals
    if total == 0:
        return "keyword"
    keyword_ratio = keyword_signals / total
    if keyword_ratio >= 0.5:
        return "keyword"
    elif keyword_ratio <= 0.2:
        return "semantic"
    return "hybrid"


def classify_query(query: str, llm=None) -> Literal["keyword", "semantic", "hybrid"]:
    active_llm = llm or CLASSIFIER_LLM
    if USE_LLM_CLASSIFIER and active_llm is not None:
        return classify_query_with_llm(query, active_llm)
    return _classify_query_rules(query)


def query_router(query: str, k: int = 10, filters: dict = None) -> list:
    query_type = classify_query(query)
    icons = {"keyword": "[KW]", "semantic": "[SEM]", "hybrid": "[HYB]"}
    _log(f"[PIPELINE]   [SEARCH] Retrieval type: {icons.get(query_type, '[?]')} {query_type.upper()}")
    if query_type == "keyword":
        return bm25_search(query, k=k, filters=filters)
    elif query_type == "semantic":
        return semantic_search(query, k=k, filters=filters)
    else:
        return hybrid_retrieve(query, k=k, filters=filters)


def generate_query_variations(query: str, llm=None, n: int = 3, domain_vocab: dict = None) -> list:
    if llm is None:
        return [query]
    try:
        catalog_hint = ""
        if domain_vocab:
            product_types = domain_vocab.get("products", [])[:40]
            subcategories = domain_vocab.get("subcategories", [])
            if product_types or subcategories:
                catalog_hint = (
                    f"\nThe catalog contains these product types: {', '.join(product_types)}."
                    f"\nAnd these subcategories: {', '.join(subcategories)}."
                    f"\nWhen generating variations, include any catalog terms that are semantically related to the query."
                )
        prompt = (
            f"Generate {n} diverse search queries for a fashion product catalog based on: \"{query}\""
            f"{catalog_hint}"
            f"\nReturn exactly one query per line, no numbering or bullets."
        )
        resp = llm.invoke([HumanMessage(content=prompt)])
        lines = [ln.strip() for ln in resp.content.splitlines() if ln.strip()]
        if query not in lines:
            lines.insert(0, query)
        return lines[:n]
    except Exception:
        return [query]


def rag_fusion_retrieve(query: str, k: int = 10, filters: dict = None, original_docs: list = None) -> tuple:
    variations = generate_query_variations(query, llm=light_llm, n=3, domain_vocab=routing_config.get('domain_vocab'))
    if filters:
        _log(f"[RETRIEVAL] [FILTER] Applying filters across {len(variations)} variations: {filters}")
    all_results = [query_router(q, k=k, filters=filters) for q in variations]
    doc_scores = {}
    for result_set in all_results:
        for rank, doc in enumerate(result_set):
            doc_id = doc.get("id")
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {"doc": doc, "appearances": 0, "rrf_score": 0.0}
            doc_scores[doc_id]["appearances"] += 1
            doc_scores[doc_id]["rrf_score"] += 1.0 / (60 + rank + 1)
    for doc_id, data in doc_scores.items():
        intersection_boost = 1.0 + 0.5 * (data["appearances"] - 1)
        data["final_score"] = data["rrf_score"] * intersection_boost
        data["doc"]["fusion_score"] = data["final_score"]
        data["doc"]["fusion_appearances"] = data["appearances"]
    sorted_docs = sorted(doc_scores.values(), key=lambda x: x["final_score"], reverse=True)
    fused_docs = [item["doc"] for item in sorted_docs[:k]]
    return fused_docs, variations


# =============================================================================
# REFLECTION (Relevance Check)
# =============================================================================

def check_relevance(query: str, docs: list, llm=None, threshold: float = 0.3) -> dict:
    if not docs:
        return {"is_relevant": False, "reason": "no_docs", "score": 0}
    if llm is None:
        return {"is_relevant": True, "reason": "no_llm_configured", "score": 1}

    doc_snippets = []
    for i, d in enumerate(docs[:5], 1):
        metadata = d.get("metadata", {})
        snippet = (f"Doc {i}: {metadata.get('ProductTitle', 'N/A')} | "
                   f"{metadata.get('Gender', '')} | {metadata.get('Colour', '')}\n"
                   f"{d['text'][:400]}")
        doc_snippets.append(snippet)
    documents = "\n\n".join(doc_snippets)

    system = """You are a relevance grader for a product search system.
Be LENIENT - if the products are in the right category or have relevant attributes, they are useful.
Score on a scale of 0-10:
- 0-2: Completely irrelevant
- 3-5: Partially relevant
- 6-8: Relevant
- 9-10: Highly relevant
Respond in this format:
Score: <0-10>
Explanation: <brief reasoning>"""

    user = f"User question: {query}\n\nRetrieved products:\n{documents}\n\nScore the relevance (0-10):"

    try:
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)]).content
        score_match = re.search(r'score[:\s]*([0-9]+)', resp.lower())
        score = int(score_match.group(1)) if score_match else 5
        normalized_score = score / 10.0
        resp_lower = resp.lower()
        explanation = (resp[resp_lower.find("explanation:") + len("explanation:"):].strip()
                       if "explanation:" in resp_lower else resp)
        is_relevant = normalized_score >= threshold
        _log(f"[PIPELINE]   [STATS] Relevance: {score}/10 ({'[OK] relevant' if is_relevant else '[ERR] not relevant'})")
        return {"is_relevant": is_relevant, "reason": explanation[:200], "score": normalized_score}
    except Exception as e:
        _log(f"[PIPELINE]   [WARN] Relevance check error: {str(e)[:50]}")
        return {"is_relevant": True, "reason": f"llm_error: {str(e)[:50]}", "score": 0.5}


# =============================================================================
# COMPANY INFO & PERSONA
# =============================================================================

COMPANY_INFO = {
    "name": "Fashion Store",
    "description": "Your one-stop shop for trendy fashion items for the whole family.",
    "categories": ["Men's Wear", "Women's Wear", "Kids' Wear", "Footwear", "Accessories"],
    "tone": "friendly, helpful, fashion-forward",
    "policies": {
        "returns": "30-day return policy on unworn items",
        "shipping": "Free shipping on orders over $50",
    },
    "context_schema": {
        "item_label": "Product",
        "id_field": "ProductId",
        "title_field": "ProductTitle",
        "display_fields": [
            ("ProductTitle", "Title", False),
            ("ProductBrand", "Brand", True),
            ("Colour", "Color", True),
            ("Gender", "Gender", True),
            ("Category", "Category", True),
            ("SubCategory", "Subcategory", True),
            ("Price", "Price", True),
            ("ImageURL", "Image Link", True),
        ],
        "include_text": False,
    }
}

PERSONA = {
    "brand_voice": "friendly, trendy, and approachable",
    "brand_values": ["quality", "affordability", "style for everyone"],
    "target_audience": {
        "demographics": "young adults and families",
        "interests": ["fashion", "trends", "value shopping"],
        "communication_preference": "casual, not overly formal",
    },
    "tone": "warm, helpful, and enthusiastic without being pushy",
    "language_style": "conversational, uses simple language, avoids jargon",
    "do": [
        "Be genuinely helpful and recommend products that fit their needs",
        "Use casual, friendly language that matches the brand vibe",
        "Mention specific product details (color, style, price when relevant)",
        "Acknowledge when you don't have what they're looking for",
        "Keep responses concise - respect their time",
    ],
    "use_emojis": True,
    "dont": [
        "Be overly salesy or pushy",
        "Use formal/corporate language",
        "Make up information about products",
        "Ignore the customer's specific requirements",
    ],
}


def load_company_info(company_id: str = None) -> dict:
    return COMPANY_INFO


_PERSONA_PATH = Path(__file__).parent.parent / "Persona Module" / "final_persona.json"

_EMOJI_TONES = {"conversational", "expressive", "playful", "warm", "casual", "enthusiastic", "friendly"}


def _persona_uses_emojis(emotional_tone: str) -> bool:
    """Return True if the persona's tone suggests emoji use is appropriate."""
    return any(t in emotional_tone.lower() for t in _EMOJI_TONES)


def load_persona(persona_id: str = None) -> dict:
    if _PERSONA_PATH.exists():
        try:
            with open(_PERSONA_PATH, encoding="utf-8") as _f:
                _p = json.load(_f)
            archetype = _p.get("archetype", "")
            emotional_tone = _p.get("emotional_tone", "")
            keywords = _p.get("keywords", [])
            voice_description = _p.get("voice_description", "")
            _log(f"[PIPELINE] [PERSONA] Persona loaded: {archetype} ({emotional_tone})")
            return {
                "brand_voice": voice_description,
                "brand_values": keywords,
                "use_emojis": _persona_uses_emojis(emotional_tone),
                "target_audience": {
                    "demographics": "general audience",
                    "interests": keywords,
                    "communication_preference": emotional_tone,
                },
                "tone": f"{emotional_tone} — {voice_description[:80]}",
                "language_style": ", ".join(keywords),
                "do": [
                    f"Embody the '{archetype}' archetype in your responses",
                    "Be genuinely helpful and recommend products that fit their needs",
                    "Use language that matches the brand voice description",
                    "Keep responses concise — respect their time",
                    "Mention specific product details (color, style, price when relevant)",
                ],
                "dont": [
                    "Be overly salesy or pushy",
                    "Make up information about products",
                    "Ignore the customer's specific requirements",
                ],
            }
        except Exception as _e:
            _log(f"[PIPELINE] [WARN] Could not load final_persona.json ({_e}) — using default persona")
    return PERSONA


# =============================================================================
# GENERATION
# =============================================================================

FALLBACK_PROMPT_TEMPLATE = """# Your Role
You are a customer service assistant for {company_name}.

# Brand Voice
{brand_voice}

# Situation
The user asked a question, but no relevant products were found in our catalog.

# Instructions
- Acknowledge you couldn't find exactly what they're looking for
- Suggest alternatives or ask clarifying questions
- Stay helpful and on-brand

# User Question
{question}

# Your Response
"""

PROMPT_VARIANTS = {
    "product": {
        "knowledge_label": "Retrieved Products",
        "instructions": "\n".join([
            "Answer the user's question using ONLY the retrieved product information.",
            "- Be warm, friendly, and conversational (helpful shop-assistant tone)",
            "- Understand what the user really needs",
            "- Recommend the most relevant products from the context",
            "- Write naturally, not as a list (unless they asked for options)",
            "- Include specific details (name, color, price when relevant)",
            "- Mention product IDs only when a product name is unavailable",
            "- If no relevant products found, acknowledge honestly and suggest alternatives",
            "- If a product has an Image Link, put it on its own line as a plain URL — no markdown, no [text](url) syntax",
            "- When mentioning multiple products, separate each one with a blank line for easy reading",
            "- Do NOT use any markdown formatting — no *bold*, no _italic_, no [text](url) links",
            "- Answer ONLY the user's current question — do NOT bring up or reference previous topics from chat history unless the user explicitly asks about them",
        ]),
    },
    "company": {
        "knowledge_label": "Company Knowledge",
        "instructions": "\n".join([
            "Answer the user's message using ONLY the company knowledge provided.",
            "- If the user is greeting you (e.g. 'Hi', 'Hello'), respond with a warm welcome, "
            "introduce the store briefly, and invite them to ask about products or anything else you can help with",
            "- For company questions, be clear, concise, and policy-accurate",
            "- If details are missing, say what is unknown and suggest next steps",
            "- Do not invent policies, prices, delivery promises, or guarantees",
            "- Keep the response practical, friendly, and customer-friendly",
        ]),
    },
}


def format_context(docs: list, company_info: dict = None, max_docs: int = 5,
                   include_all_metadata: bool = True) -> str:
    if not docs:
        return "No items found."
    if company_info and "context_schema" in company_info:
        schema = company_info["context_schema"]
    else:
        schema = {"item_label": "Item", "title_field": None, "display_fields": None, "include_text": True}

    item_label = schema.get("item_label", "Item")
    display_fields = schema.get("display_fields")
    include_text = schema.get("include_text", False)

    formatted = []
    for i, doc in enumerate(docs[:max_docs], 1):
        metadata = doc.get("metadata", {})
        text = doc.get("text", "")
        item_info = f"{item_label} {i}:\n"

        if display_fields:
            for field_config in display_fields:
                if isinstance(field_config, tuple):
                    field_name, display_label, optional = field_config
                else:
                    field_name = field_config
                    display_label = field_config
                    optional = True
                value = metadata.get(field_name)
                if value or not optional:
                    item_info += f"  {display_label}: {value or 'N/A'}\n"
        else:
            for key, value in metadata.items():
                if value and key not in ['source', 'row']:
                    display_label = ''.join(' ' + c if c.isupper() else c for c in key).strip()
                    item_info += f"  {display_label}: {value}\n"

        if include_all_metadata and metadata:
            seen_keys = set()
            if display_fields:
                for field_config in display_fields:
                    field_name = field_config[0] if isinstance(field_config, tuple) else field_config
                    seen_keys.add(field_name)
            remaining = []
            for key, value in metadata.items():
                if key in ['source', 'row'] or key in seen_keys or not value:
                    continue
                display_label = ''.join(' ' + c if c.isupper() else c for c in key).strip()
                remaining.append(f"  {display_label}: {value}")
            if remaining:
                item_info += "  Full Metadata:\n" + "\n".join(remaining) + "\n"

        # Append product link if available and not already shown via display_fields
        if not display_fields:
            image_url = (metadata.get("ImageURL") or metadata.get("link")
                         or metadata.get("permalink_url"))
            if image_url:
                item_info += f"  Link: {image_url}\n"

        if include_text and text:
            item_info += f"  Description: {text[:200]}...\n" if len(text) > 200 else f"  Description: {text}\n"

        formatted.append(item_info)
    return "\n".join(formatted)


def format_chat_history(history: list, max_turns: int = 5) -> str:
    if not history:
        return "(No previous conversation)"
    formatted = []
    for msg in history[-max_turns * 2:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted.append(f"{role.capitalize()}: {content}")
    return "\n".join(formatted) if formatted else "(No previous conversation)"


def build_assistant_prompt(route: str, *, company_name: str, company_description: str,
                           brand_voice: str, tone: str, do_guidelines: str, dont_guidelines: str,
                           target_audience: str, chat_history: str, question: str,
                           knowledge_payload: str) -> str:
    variant = PROMPT_VARIANTS.get(route, PROMPT_VARIANTS["product"])
    knowledge_block = (f"# {variant['knowledge_label']}\n<context>\n{knowledge_payload}\n</context>")
    return """# Your Role
You are a customer service assistant for {company_name}.
{company_description}

# Brand Voice & Tone
{brand_voice}
{tone}

# Communication Guidelines
DO:
{do_guidelines}

DON'T:
{dont_guidelines}

# Target Audience
{target_audience}

# Knowledge
{knowledge_block}

# Instructions
{instructions_block}

# Chat History
{chat_history}

# User Question
{question}

# Your Response
""".format(
        company_name=company_name, company_description=company_description,
        brand_voice=brand_voice, tone=tone, do_guidelines=do_guidelines,
        dont_guidelines=dont_guidelines, target_audience=target_audience,
        knowledge_block=knowledge_block, instructions_block=variant["instructions"],
        chat_history=chat_history, question=question,
    )


def build_company_route_prompt(query: str, company_context: str, chat_history: list = None,
                               company_info: dict = None, persona: dict = None) -> str:
    company = company_info or load_company_info()
    persona_cfg = persona or load_persona()
    do_guidelines = "\n".join(f"- {g}" for g in persona_cfg.get("do", []))
    if persona_cfg.get("use_emojis"):
        do_guidelines += "\n- Use relevant emojis naturally (e.g., ✨ 😊) to make responses feel warm and engaging"
    dont_guidelines = "\n".join(f"- {g}" for g in persona_cfg.get("dont", []))
    target_aud = persona_cfg.get("target_audience", {})
    target_audience_str = (f"Demographics: {target_aud.get('demographics', 'general')}\n"
                           f"Communication: {target_aud.get('communication_preference', 'friendly')}")
    return build_assistant_prompt(
        route="company",
        company_name=company.get("name", "Our Store"),
        company_description=company.get("description", ""),
        brand_voice=f"Voice: {persona_cfg.get('brand_voice', 'helpful and friendly')}",
        tone=f"Tone: {persona_cfg.get('tone', 'warm and professional')}",
        do_guidelines=do_guidelines or "- Be helpful",
        dont_guidelines=dont_guidelines or "- Don't be pushy",
        target_audience=target_audience_str,
        chat_history=format_chat_history(chat_history),
        question=query,
        knowledge_payload=company_context or "No company knowledge provided.",
    )


def generate_response(query: str, docs: list, chat_history: list = None,
                      company_info: dict = None, persona: dict = None, llm=None) -> dict:
    llm = llm or good_llm
    company = company_info or load_company_info()
    persona_cfg = persona or load_persona()

    if llm is None:
        return {"response": "I'm sorry, I can't generate a response right now.", "sources": [], "status": "error_no_llm"}

    context = format_context(docs, company_info=company, include_all_metadata=True)
    history_str = format_chat_history(chat_history)
    do_guidelines = "\n".join(f"- {g}" for g in persona_cfg.get("do", []))
    if persona_cfg.get("use_emojis"):
        do_guidelines += "\n- Use relevant emojis naturally (e.g., ✨ 👗 👕 👟 😊) to make responses feel warm and engaging"
    dont_guidelines = "\n".join(f"- {g}" for g in persona_cfg.get("dont", []))
    target_aud = persona_cfg.get("target_audience", {})
    target_audience_str = (f"Demographics: {target_aud.get('demographics', 'general')}\n"
                           f"Communication: {target_aud.get('communication_preference', 'friendly')}")

    if docs:
        prompt = build_assistant_prompt(
            route="product",
            company_name=company.get("name", "Our Store"),
            company_description=company.get("description", ""),
            brand_voice=f"Voice: {persona_cfg.get('brand_voice', 'helpful and friendly')}",
            tone=f"Tone: {persona_cfg.get('tone', 'warm and professional')}",
            do_guidelines=do_guidelines or "- Be helpful",
            dont_guidelines=dont_guidelines or "- Don't be pushy",
            target_audience=target_audience_str,
            knowledge_payload=context,
            chat_history=history_str,
            question=query,
        )
    else:
        prompt = FALLBACK_PROMPT_TEMPLATE.format(
            company_name=company.get("name", "Our Store"),
            brand_voice=f"Voice: {persona_cfg.get('brand_voice', 'helpful and friendly')}",
            question=query
        )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        schema = company.get("context_schema", {})
        title_field = schema.get("title_field", "ProductTitle")
        id_field = schema.get("id_field", "ProductId")
        sources = []
        for doc in docs:
            metadata = doc.get("metadata", {})
            text = doc.get("text", "") or ""
            parsed_title = None
            if text.lower().startswith("the product ") and " is " in text:
                parsed_title = text[len("The product "):text.find(" is ")].strip()
            sources.append({
                "id": metadata.get(id_field) or metadata.get("ProductId") or metadata.get("id"),
                "title": metadata.get(title_field) or metadata.get("ProductTitle") or parsed_title,
                "metadata": metadata,
                "text": text,
                "source": doc.get("source"),
                "score": doc.get("score", doc.get("final_score")),
            })
        return {"response": response.content.strip(), "sources": sources,
                "status": "success" if docs else "no_context"}
    except Exception as e:
        _log(f"[PIPELINE] [WARN] Generation failed: {str(e)[:50]}")
        return {"response": "I apologize, but I encountered an issue. Please try again.",
                "sources": [], "status": f"error: {str(e)[:50]}"}


# =============================================================================
# LANGGRAPH RETRIEVAL SUBGRAPH
# =============================================================================

class RetrievalState(TypedDict, total=False):
    query: str
    metadata_filters: Optional[dict]
    route: Optional[str]
    chat_history: Optional[list]
    use_fusion: bool
    fusion_queries: list
    is_relevant: bool
    retrieved_docs: list
    retrieval_status: str
    relevance_reason: str
    generated_response: Optional[str]
    generation_status: Optional[str]
    sources: Optional[list]


def retrieve_node(state: RetrievalState) -> dict:
    query = state["query"]
    filters = state.get("metadata_filters")
    if state.get("use_fusion"):
        _log("[PIPELINE] [ROUTE] RAG Fusion: generating query variations...")
        original_docs = state.get("retrieved_docs", [])
        docs, variations = rag_fusion_retrieve(query, k=10, filters=filters, original_docs=original_docs)
        _log(f"[PIPELINE] [DOCS] Fusion retrieved {len(docs)} docs")
        return {"retrieved_docs": docs, "fusion_queries": variations}
    else:
        if filters:
            _log(f"[RETRIEVAL] [FILTER] Applying filters: {filters}")
        else:
            _log("[RETRIEVAL] [FILTER] No filters — full unfiltered retrieval")
        _log("[PIPELINE] [SEARCH] Retrieving docs (single query)...")
        docs = query_router(query, k=10, filters=filters)
        _log(f"[PIPELINE] [DOCS] Retrieved {len(docs)} docs")
        return {"retrieved_docs": docs}


def reflect_node(state: RetrievalState) -> dict:
    _log("[PIPELINE] [EVAL] Reflecting on relevance...")
    result = check_relevance(state["query"], state.get("retrieved_docs", []), llm=good_llm)
    return {"is_relevant": result["is_relevant"], "relevance_reason": result["reason"]}


def enable_fusion_node(state: RetrievalState) -> dict:
    return {"use_fusion": True}


def finalize_node(state: RetrievalState) -> dict:
    if state.get("is_relevant", False):
        status = "fusion_used" if state.get("use_fusion") else "success"
        return {"retrieved_docs": state.get("retrieved_docs", []), "retrieval_status": status}
    else:
        return {"retrieval_status": "no_relevant_docs", "retrieved_docs": []}


def should_fuse(state: RetrievalState) -> str:
    if state.get("is_relevant", False):
        return "finalize"
    if not state.get("use_fusion"):
        return "fuse"
    return "finalize"


retrieval_builder = StateGraph(RetrievalState)
retrieval_builder.add_node("retrieve", retrieve_node)
retrieval_builder.add_node("reflect", reflect_node)
retrieval_builder.add_node("enable_fusion", enable_fusion_node)
retrieval_builder.add_node("finalize", finalize_node)
retrieval_builder.add_edge(START, "retrieve")
retrieval_builder.add_edge("retrieve", "reflect")
retrieval_builder.add_conditional_edges("reflect", should_fuse,
                                        {"finalize": "finalize", "fuse": "enable_fusion"})
retrieval_builder.add_edge("enable_fusion", "retrieve")
retrieval_builder.add_edge("finalize", END)
retrieval_graph = retrieval_builder.compile()

retrieval_subgraph = retrieval_graph  # alias for external use


# =============================================================================
# ORCHESTRATION GRAPH
# =============================================================================

def _normalize_route(route_value: Any) -> str:
    if route_value is None:
        return "2"
    try:
        if route_value == QueryRoute.IRRELEVANT:
            return "0"
        if route_value == QueryRoute.COMPANY_RELATED:
            return "1"
        if route_value == QueryRoute.PRODUCT_QUERY:
            return "2"
    except Exception:
        pass
    route_str = str(route_value).strip().lower()
    if route_str in {"0", "irrelevant", "irrelevant_question", "template", "queryroute.irrelevant"}:
        return "0"
    if route_str in {"1", "company", "generic", "company_related", "queryroute.company_related"}:
        return "1"
    return "2"


_FOLLOWUP_RE = re.compile(
    r'^(more|show more|more options?|what else|another|others?|other options?|'
    r'give me more|any more|show me more|anything else|keep going|continue|next|'
    r'tell me more|more products?|more items?|more choices?|yes please|ok|okay|sure|'
    r'sounds good|great|go ahead|show me|i want more)\??\.?$',
    re.IGNORECASE,
)


def _is_followup(query: str) -> bool:
    stripped = query.strip()
    # Greetings are never follow-ups — never contextualize them
    if _GREETING_RE.match(stripped):
        return False
    # Only trigger on explicit follow-up phrases (e.g. "more", "show me more").
    # Length-based rules are unreliable: short words like "slippers" or "bonjour"
    # are not follow-ups and must not be contextualized.
    return bool(_FOLLOWUP_RE.match(stripped))


def contextualize_query(query: str, chat_history: list) -> str:
    """
    If the query looks like a follow-up, rewrite it as a self-contained question
    using the recent chat history. Returns the original query if not needed.
    """
    if not chat_history or not _is_followup(query):
        return query

    history_str = format_chat_history(chat_history, max_turns=3)
    prompt = (
        f"Conversation so far:\n{history_str}\n\n"
        f"User's latest message: \"{query}\"\n\n"
        "Rewrite the user's message as a complete, self-contained request using the conversation context.\n"
        "Rules:\n"
        "- If the message is an affirmative (yes / sure / ok / okay / go ahead / sounds good / great), "
        "rephrase it as the action the bot's last question was offering. "
        "Example: bot asked 'Would you like me to find alternatives?' + user says 'sure' → "
        "'Please find alternatives for [product from conversation]'.\n"
        "- If it continues the same topic, rewrite as a complete standalone request.\n"
        "- If it introduces a NEW topic or different product, return it EXACTLY as written.\n"
        "Return ONLY the rewritten request, nothing else."
    )
    try:
        result = light_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        return result if result else query
    except Exception:
        return query


def contextualize_node(state: dict) -> dict:
    """Expand follow-up queries (e.g. 'more options') into full standalone questions."""
    query = state.get("query", "")
    chat_history = state.get("chat_history") or []
    if not chat_history:
        return {}
    expanded = contextualize_query(query, chat_history)
    if expanded != query:
        _log(f"[PIPELINE] [CONTEXT] Context: \"{query}\" → \"{expanded}\"")
        return {"query": expanded}
    return {}


def pre_retrieval_router_node(state: dict) -> dict:
    query = state.get("query", "")
    if _GREETING_RE.match(query.strip()):
        greeting_template = routing_config.get(
            "greeting_template",
            "Hi {{username}}! Welcome! How can I help you today? 😊"
        )
        username = state.get("username", "") or ""
        first_name = username.split()[0] if username else "there"
        greeting_text = greeting_template.replace("{{username}}", first_name)
        _log("[PIPELINE] [ROUTE] Route: GREETING (0)")
        return {
            "route": "0",
            "compressed_query": query,
            "metadata_filters": {},
            "ready_template_answer": greeting_text,
            "routing_response": greeting_text,
            "company_response": None,
        }

    if state.get("route") is not None:
        normalized = _normalize_route(state.get("route"))
        route_names = {"0": "IRRELEVANT", "1": "COMPANY_RELATED", "2": "PRODUCT_QUERY"}
        _log(f"[PIPELINE] [ROUTE] Route: {route_names.get(normalized, '?')} ({normalized})")
        return {"route": normalized}

    routing_state = routing_graph.invoke({
        "original_query": state.get("query", ""),
        "query": state.get("query", ""),
        "compressed_query": None,
        "route": None,
        "username": state.get("username", "Customer"),
        "response": None,
        "company_response": None,
        "metadata_filters": state.get("metadata_filters"),
    })
    normalized = _normalize_route(routing_state.get("route"))
    route_names = {"0": "IRRELEVANT", "1": "COMPANY_RELATED", "2": "PRODUCT_QUERY"}
    _log(f"[PIPELINE] [ROUTE] Route: {route_names.get(normalized, '?')} ({normalized})")
    compressed = routing_state.get("compressed_query")
    original = state.get("query", "")
    if compressed and compressed != original:
        _log(f"[PIPELINE] [COMPRESS] Compressed: \"{original}\" → \"{compressed}\"")
    return {
        "route": normalized,
        "compressed_query": routing_state.get("compressed_query"),
        "metadata_filters": state.get("metadata_filters") or routing_state.get("metadata_filters"),
        "routing_response": routing_state.get("response"),
        "company_response": state.get("company_response") or routing_state.get("company_response"),
    }


def route_decision(state: dict) -> str:
    route = _normalize_route(state.get("route"))
    if route == "0":
        return "irrelevant"
    if route == "1":
        return "company"
    return "product"


def irrelevant_template_node(state: dict) -> dict:
    is_greeting = bool(_GREETING_RE.match(state.get("query", "").strip()))
    _log(f"[PIPELINE] {'Greeting' if is_greeting else 'Irrelevant query'} → returning template response")
    fallback_from_route = route_0_irrelevant_query(
        state.get("query", ""), state.get("username") or ""
    ).get("response", "")
    template_answer = (
        state.get("ready_template_answer")
        or state.get("irrelevant_template")
        or state.get("template_answer")
        or state.get("routing_response")
        or fallback_from_route
        or routing_config.get("irrelevant_template", "")
        or "Sorry, this question is outside what I can help with here."
    )
    _log(f"[PIPELINE] [MSG] Response ({len(template_answer)} chars)")
    _log(f"[PIPELINE]    \"{template_answer[:200]}{'...' if len(template_answer) > 200 else ''}\"")
    return {
        "generated_response": template_answer,
        "generation_status": "skipped_template",
        "retrieval_status": "skipped_irrelevant",
        "sources": [],
        "retrieved_docs": [],
    }


def _format_company_value(value: Any) -> str:
    if isinstance(value, list):
        if not value:
            return ""
        if all(isinstance(item, dict) for item in value):
            lines = []
            for item in value:
                if "city" in item and "address" in item:
                    lines.append(f"- {item.get('city')}: {item.get('address')}")
                else:
                    parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in item.items()]
                    lines.append(f"- {' | '.join(parts)}")
            return "\n".join(lines)
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return "\n".join(f"- {k.replace('_', ' ').title()}: {v}" for k, v in value.items())
    return str(value)


def company_answer_node(state: dict) -> dict:
    _log("[PIPELINE] [INFO] Company query → generating company answer")
    company_payload = state.get("company_response")
    if not company_payload:
        company_payload = route_1_company_query(state.get("query", "")).get("company_response", {})

    lines = []
    if isinstance(company_payload, dict) and company_payload:
        for key, value in list(company_payload.items()):
            if key in {"persona_context", "persona", "personaContext"}:
                continue
            pretty_value = _format_company_value(value)
            if pretty_value:
                lines.append(
                    f"{key.replace('_', ' ').title()}:\n{pretty_value}"
                    if "\n" in pretty_value
                    else f"{key.replace('_', ' ').title()}: {pretty_value}"
                )
            if len(lines) >= 6:
                break
    company_context = "\n\n".join(lines)
    company_answer = state.get("company_answer")
    generation_status = "skipped_company_pass_through"

    if not company_answer:
        if good_llm is not None and company_context:
            try:
                prompt = build_company_route_prompt(
                    query=state.get("query", ""),
                    company_context=company_context,
                    chat_history=state.get("chat_history", []),
                    company_info=load_company_info(),
                    persona=load_persona(),
                )
                llm_response = good_llm.invoke([HumanMessage(content=prompt)])
                company_answer = (llm_response.content or "").strip()
                if company_answer:
                    generation_status = "success_company_llm"
            except Exception as e:
                _log(f"[PIPELINE] [WARN] Company route generation failed: {str(e)[:80]}")

        if not company_answer:
            if company_context:
                company_answer = (
                    "Happy to help! Here are the details you asked for:\n\n"
                    + company_context
                    + "\n\nIf you want, I can also give you a shorter summary or focus on one specific detail."
                )
            else:
                company_answer = (
                    state.get("generic_answer")
                    or "Happy to help! I can share details about our stores, contact information, and company background."
                )

    _log(f"[PIPELINE] [MSG] Response ({len(company_answer)} chars) | status={generation_status}")
    _log(f"[PIPELINE]    \"{company_answer[:200]}{'...' if len(company_answer) > 200 else ''}\"")
    return {
        "generated_response": company_answer,
        "generation_status": generation_status,
        "retrieval_status": "skipped_company",
        "company_response": company_payload,
        "sources": [],
        "retrieved_docs": [],
    }


def product_retrieval_node(state: dict) -> dict:
    _log("[PIPELINE] [SEARCH] Product query → starting retrieval...")
    query_text = state.get("compressed_query") or state.get("query", "")
    result = retrieval_graph.invoke({
        "query": query_text,
        "metadata_filters": state.get("metadata_filters"),
        "route": "2",
        "chat_history": state.get("chat_history", []),
    })
    return {
        "retrieved_docs": result.get("retrieved_docs", []),
        "retrieval_status": result.get("retrieval_status", "unknown"),
        "relevance_reason": result.get("relevance_reason", ""),
    }


class OrchestrationState(TypedDict, total=False):
    query: str
    route: Optional[Any]
    metadata_filters: Optional[dict]
    compressed_query: Optional[str]
    chat_history: Optional[list]
    username: Optional[str]
    ready_template_answer: Optional[str]
    irrelevant_template: Optional[str]
    template_answer: Optional[str]
    routing_response: Optional[str]
    company_answer: Optional[str]
    company_response: Optional[Any]
    generic_answer: Optional[str]
    retrieved_docs: list
    retrieval_status: str
    relevance_reason: str
    generated_response: str
    generation_status: str
    sources: list
    retry_count: int


def generate_node(state: dict) -> dict:
    _log("[PIPELINE] [GEN] Generating response...")
    result = generate_response(
        query=state.get("query", ""),
        docs=state.get("retrieved_docs", []),
        chat_history=state.get("chat_history", []),
        company_info=load_company_info(),
        persona=load_persona(),
        llm=generation_llm,
    )
    response_text = result.get("response", "")
    _log(f"[PIPELINE] [MSG] Response ({len(response_text)} chars) | status={result.get('status')}")
    _log(f"[PIPELINE]    \"{response_text[:200]}{'...' if len(response_text) > 200 else ''}\"")
    return {
        "generated_response": response_text,
        "sources": result.get("sources", []),
        "generation_status": result.get("status", "unknown"),
    }


MAX_RETRIES = 2


def validate_response(response: str, docs: list) -> tuple:
    """Returns (is_valid, reason). Catches empty, too-short, or apologetic responses."""
    if not response or len(response.strip()) < 20:
        return False, "response_too_short"
    apologetic_phrases = [
        "i cannot help", "i can't help", "no relevant",
        "i don't have information", "i'm sorry, i cannot", "sorry, i can't",
    ]
    if docs and any(phrase in response.lower() for phrase in apologetic_phrases):
        return False, "apologetic_with_docs"
    return True, "ok"


def validate_node(state: dict) -> dict:
    """Guardrail node — validates generated response and signals retry if needed."""
    response = state.get("generated_response", "")
    docs = state.get("retrieved_docs", [])
    retry_count = state.get("retry_count", 0)
    is_valid, reason = validate_response(response, docs)
    if not is_valid:
        _log(f"[PIPELINE] [WARN] Validation failed ({reason}) — retry {retry_count + 1}/{MAX_RETRIES}")
    else:
        _log(f"[PIPELINE] [OK] Response validated")
    return {
        "retry_count": retry_count + (0 if is_valid else 1),
        "generation_status": "valid" if is_valid else f"invalid_{reason}",
    }


def validation_decision(state: dict) -> str:
    """Route back to generate if response is invalid and retries remain."""
    status = state.get("generation_status", "")
    retry_count = state.get("retry_count", 0)
    if status.startswith("invalid") and retry_count < MAX_RETRIES:
        return "retry"
    return "done"


orchestration_builder = StateGraph(OrchestrationState)
orchestration_builder.add_node("contextualize", contextualize_node)
orchestration_builder.add_node("pre_router", pre_retrieval_router_node)
orchestration_builder.add_node("irrelevant_template", irrelevant_template_node)
orchestration_builder.add_node("company_answer", company_answer_node)
orchestration_builder.add_node("product_retrieval", product_retrieval_node)
orchestration_builder.add_node("generate", generate_node)
orchestration_builder.add_node("validate", validate_node)
orchestration_builder.add_edge(START, "contextualize")
orchestration_builder.add_edge("contextualize", "pre_router")
orchestration_builder.add_conditional_edges("pre_router", route_decision, {
    "irrelevant": "irrelevant_template",
    "company": "company_answer",
    "product": "product_retrieval",
})
orchestration_builder.add_edge("irrelevant_template", END)
orchestration_builder.add_edge("company_answer", END)
orchestration_builder.add_edge("product_retrieval", "generate")
orchestration_builder.add_edge("generate", "validate")
orchestration_builder.add_conditional_edges("validate", validation_decision, {
    "retry": "generate",
    "done": END,
})
assistant_graph = orchestration_builder.compile()


def product_query_node(state: dict) -> dict:
    result = assistant_graph.invoke(state)
    return {
        **state,
        "generated_response": result.get("generated_response", ""),
        "sources": result.get("sources", []),
        "retrieved_docs": result.get("retrieved_docs", []),
        "retrieval_status": result.get("retrieval_status", "unknown"),
        "generation_status": result.get("generation_status", "unknown"),
        "relevance_reason": result.get("relevance_reason", ""),
        "route": _normalize_route(result.get("route", state.get("route"))),
    }


_log("[PIPELINE] [OK] Chatbot pipeline ready!")


# =============================================================================
# PUBLIC API
# =============================================================================

def retrieve_only(query: str, k: int = 10, filters: dict = None) -> list:
    """Direct retrieval without reflection or generation."""
    return query_router(query, k=k, filters=filters)


def run_full_pipeline(
    query: str,
    metadata_filters: dict = None,
    chat_history: list = None,
    route: str = "2",
    ready_template_answer: str = None,
    company_answer: str = None,
    username: str = None,
    _is_subquery: bool = False,
) -> dict:
    """
    Run the full chatbot pipeline: routing → retrieval → reflection → generation.

    Args:
        query: User's message
        metadata_filters: Optional product filters (e.g. {"Gender": "Girls"})
        chat_history: List of {"role": "user"/"assistant", "content": "..."} dicts
        route: Override route ("0"=irrelevant, "1"=company, "2"=product). Default "2".
        ready_template_answer: Pre-built template for route 0
        company_answer: Pre-built answer for route 1
        username: Display name of the user (used in template responses)

    Returns:
        dict with keys: response, sources, retrieval_status, generation_status,
                        retrieved_docs, relevance_reason, route
    """
    _log(f'[PIPELINE] {"=" * 60}')
    _log(f'[PIPELINE] >> Query: "{query[:100]}"')

    # Multi-intent detection: split into sub-queries and process each independently
    if not _is_subquery:
        parts = split_query(query)
        if len(parts) > 1:
            _log(f'[PIPELINE] [SPLIT] Multi-intent query — {len(parts)} parts detected')
            responses = []
            for i, part in enumerate(parts, 1):
                _log(f'[PIPELINE] ├─ Sub-query {i}/{len(parts)}: "{part}"')
                sub = run_full_pipeline(
                    query=part,
                    metadata_filters=metadata_filters,
                    chat_history=chat_history,
                    route=None,
                    username=username,
                    _is_subquery=True,
                )
                if sub.get("response"):
                    responses.append(sub["response"])
            return {
                "response": "\n\n".join(responses),
                "sources": [],
                "retrieval_status": "multi",
                "generation_status": "success",
                "retrieved_docs": [],
                "relevance_reason": "",
                "route": "multi",
            }

    result = assistant_graph.invoke({
        "query": query,
        "metadata_filters": metadata_filters,
        "route": route,
        "chat_history": chat_history or [],
        "ready_template_answer": ready_template_answer,
        "company_answer": company_answer,
        "username": username.split()[0] if username else "",
    })

    return {
        "response": result.get("generated_response", ""),
        "sources": result.get("sources", []),
        "retrieval_status": result.get("retrieval_status", "unknown"),
        "generation_status": result.get("generation_status", "unknown"),
        "retrieved_docs": result.get("retrieved_docs", []),
        "relevance_reason": result.get("relevance_reason", ""),
        "route": result.get("route", route),
    }

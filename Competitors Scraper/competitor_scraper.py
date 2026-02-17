"""
Competitor Scraper Module - Refactored for pipeline use
"""

import json
import time
import re
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

from openai import OpenAI
from ddgs import DDGS

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# DATA MODEL
# =============================================================================

@dataclass
class Competitor:
    name: str = ""
    facebook_url: str = ""
    facebook_username: str = ""
    instagram_handle: str = ""
    website: str = ""
    category: str = ""
    description: str = ""
    followers_approx: str = ""
    location: str = ""
    relevance_score: float = 0.0
    competitor_type: str = ""
    why_competitor: str = ""
    source: str = ""


# =============================================================================
# SEARCH ENGINE
# =============================================================================

FB_SKIP = {
    "login", "help", "groups", "watch", "marketplace", "events", "pages",
    "profile.php", "people", "photo", "photo.php", "story", "share",
    "sharer", "dialog", "hashtag", "search", "settings", "notifications",
    "messages", "gaming", "business", "ads", "privacy", "policies",
    "pg", "reel", "reels", "p", "permalink.php", "story.php",
}


def extract_fb_username(url: str) -> Optional[str]:
    """Extract Facebook page username from URL."""
    if not url or "facebook.com" not in url.lower():
        return None
    m = re.search(r"facebook\.com/([A-Za-z0-9_.]+)", url)
    if m:
        name = m.group(1)
        if name.lower() not in FB_SKIP and len(name) > 2:
            return name
    return None


class SearchEngine:
    """DuckDuckGo search using the ddgs package."""
    
    def __init__(self):
        self.total_calls = 0
        self.total_fb_pages_found = 0

    def search(self, query: str, max_results: int = 15) -> List[Dict]:
        """Run a search query."""
        self.total_calls += 1
        try:
            with DDGS() as ddg:
                raw = list(ddg.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in raw
            ]
        except Exception as e:
            logger.warning(f"   ⚠️ Search error: {e}")
            time.sleep(2)
            return []

    def search_facebook_pages(self, query: str, max_results: int = 15) -> List[Dict]:
        """Search specifically for Facebook pages."""
        results = self.search(f"site:facebook.com {query}", max_results)
        fb_results = []
        seen = set()
        for r in results:
            link = r.get("link", "")
            username = extract_fb_username(link)
            if username and username.lower() not in seen:
                seen.add(username.lower())
                r["_username"] = username
                fb_results.append(r)
                self.total_fb_pages_found += 1
        return fb_results

    def find_page_for_brand(self, brand_name: str, location: str = "") -> List[Dict]:
        """Search for a specific brand's Facebook page."""
        queries = [
            f'site:facebook.com "{brand_name}" {location}',
            f'site:facebook.com {brand_name}',
        ]
        for q in queries:
            results = self.search_facebook_pages(q, max_results=5)
            if results:
                return results
            time.sleep(0.8)
        return []


# =============================================================================
# LLM BRAIN
# =============================================================================

class Brain:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.calls = 0

    def _ask(self, prompt: str, max_tokens: int = 2000, temp: float = 0.7) -> str:
        self.calls += 1
        logger.info(f"LLM #{self.calls}")
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temp,
            )
            content = r.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            logger.error(f"❌ LLM error: {e}")
            return ""

    def _json(self, text: str):
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            pass
        m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except Exception:
                pass
        for pat in [r"\[[\s\S]*\]", r"\{[\s\S]*\}"]:
            m = re.search(pat, text)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass
        return None

    def analyze_business(self, description: str, products: str, location: str) -> Dict:
        prompt = f"""You are a competitive intelligence expert. Analyze this business:

BUSINESS: {description}
PRODUCTS/SERVICES: {products}
LOCATION: {location}

Return JSON:
{{
    "industry": "main industry",
    "niche": "specific sub-niche",
    "target_audience": "who buys",
    "keywords_en": ["10 specific search terms that would find competitor Facebook pages in English"],
    "keywords_local": ["10 search terms in the local language of {location}"],
    "search_angles": ["5 different angles to search for competitors"]
}}

Be EXTREMELY specific. Return ONLY valid JSON."""
        return self._json(self._ask(prompt)) or {}

    def generate_search_queries(self, analysis: Dict, desc: str, products: str, loc: str) -> List[str]:
        prompt = f"""Generate search queries to find Facebook pages of competitors.

ANALYSIS: {json.dumps(analysis, indent=2, ensure_ascii=False)}
BUSINESS: {desc}
PRODUCTS: {products}
LOCATION: {loc}

Generate 25 search queries. "site:facebook.com" will be added automatically.

Strategies — generate queries for EACH:
1. Specific product names + location (5 queries)
2. Industry/category + location (5 queries)
3. Local language searches (5 queries)
4. Adjacent/related products + location (5 queries)
5. Brand/shop type + location (5 queries)

RULES:
- Do NOT include "site:facebook.com" (added automatically)
- Do NOT include "facebook" in queries
- Include city/area names
- Be SPECIFIC
- Mix English and local language

Return JSON array of 25 strings: ["query1", ...]"""
        data = self._json(self._ask(prompt, max_tokens=1000))
        return data if isinstance(data, list) else []

    def recall_competitor_names(self, analysis: Dict, desc: str, products: str, loc: str) -> List[Dict]:
        """Ask LLM for competitor names."""
        prompt = f"""You are a market research expert with knowledge of businesses in {loc}.

List REAL businesses that compete with:
- Business: {desc}
- Products: {products}
- Location: {loc}
- Niche: {analysis.get('niche', '')}

For EACH competitor provide:
- name: The REAL business/brand name
- category: What they sell
- why: Why they're a competitor
- type: direct/indirect/aspirational/emerging

CRITICAL RULES:
- ONLY list businesses that ACTUALLY EXIST
- Do NOT invent or guess businesses
- Do NOT include any social media URLs or handles
- Focus on businesses in or serving {loc}

Return JSON array:
[{{"name":"...", "category":"...", "why":"...", "type":"..."}}]

Return ONLY valid JSON."""
        data = self._json(self._ask(prompt, max_tokens=3000, temp=0.7))
        return data if isinstance(data, list) else []

    def classify_search_results(self, results: List[Dict], analysis: Dict) -> List[Dict]:
        """Have LLM clean and classify raw search results."""
        if not results:
            return []

        block = "\n".join(
            f"{i+1}. Page: /{r.get('_username', '?')} | Title: {r['title'][:80]} | Snippet: {r['snippet'][:100]}"
            for i, r in enumerate(results[:30])
        )

        prompt = f"""These are Facebook pages found via search for competitors in:
Industry: {analysis.get('niche', analysis.get('industry', '?'))}
Location: Business context is about {analysis.get('target_audience', 'businesses')}

PAGES FOUND:
{block}

For each page, determine:
- name: Clean business name (remove "| Facebook", "- Home" etc.)
- relevant: true/false — is this actually a business that could be a competitor?
- category: What they sell/do
- type: direct/indirect/aspirational/emerging

SKIP pages that are personal profiles, news/media, or unrelated businesses.

Return JSON array:
[{{"index": 1, "name": "...", "relevant": true, "category": "...", "type": "..."}}]

Return ONLY valid JSON."""
        data = self._json(self._ask(prompt, max_tokens=1500))
        return data if isinstance(data, list) else []

    def expansion_queries(self, found: List[Competitor], used: List[str],
                           desc: str, products: str, loc: str) -> List[str]:
        """Generate expansion search queries based on what was already found"""
        names = [c.name for c in found[:20] if c.name]
        cats = list(set(c.category for c in found if c.category))[:10]

        prompt = f"""We searched for competitors of "{desc}" in "{loc}" and found:

COMPETITORS FOUND:
{chr(10).join(f'- {n}' for n in names[:15])}

CATEGORIES: {', '.join(cats)}

QUERIES ALREADY USED:
{chr(10).join(f'- {q}' for q in used[:12])}

Generate 10 NEW search queries to find competitors we MISSED.
Think: sub-niches, different areas within {loc}, adjacent products, local slang terms.
Do NOT include "site:facebook.com" (added automatically).

Return JSON array: ["query1", ...]

Return ONLY valid JSON."""
        data = self._json(self._ask(prompt, max_tokens=500))
        if not data:
            logger.warning("   ⚠️ Expansion queries returned empty - LLM may have failed")
            return []
        if not isinstance(data, list):
            logger.warning(f"   ⚠️ Expansion queries returned non-list: {type(data)}")
            return []
        logger.info(f"   ✅ Generated {len(data)} expansion queries")
        return data

    def score_all(self, competitors: List[Competitor], desc: str, products: str, loc: str) -> Dict[int, Dict]:
        all_scores = {}
        bs = 25

        for i in range(0, len(competitors), bs):
            batch = competitors[i:i+bs]
            items = []
            for j, c in enumerate(batch):
                line = f"{j+1}. {c.name}"
                if c.category:
                    line += f" ({c.category})"
                has_fb = "✓FB" if c.facebook_url else "no-FB"
                line += f" [{has_fb}, src:{c.source}]"
                items.append(line)

            prompt = f"""Score these as competitors to: "{desc}" selling "{products}" in "{loc}"

{chr(10).join(items)}

For each:
- score: 0.0-1.0 (how relevant as a competitor)
- type: direct/indirect/aspirational/emerging/not_relevant
- reason: one sentence

Return JSON: {{"1": {{"score": 0.8, "type": "direct", "reason": "..."}}, ...}}
ONLY valid JSON."""
            data = self._json(self._ask(prompt, max_tokens=1000))
            if data:
                for k, v in data.items():
                    try:
                        all_scores[i + int(k) - 1] = v
                    except Exception:
                        pass
        return all_scores


# =============================================================================
# COMPETITOR DISCOVERY ENGINE
# =============================================================================

class CompetitorDiscovery:
    def __init__(self, openai_key: str, model: str = "gpt-4o-mini"):
        self.brain = Brain(openai_key, model)
        self.search = SearchEngine()
        self.competitors: List[Competitor] = []
        self._seen_usernames: Set[str] = set()

    def discover(self, description: str, products: str, location: str,
                 expansion_rounds: int = 2) -> List[Competitor]:
        """
        Main discovery method - finds competitors with Facebook pages
        
        Returns:
            List of Competitor objects sorted by relevance
        """
        start = time.time()
        all_queries: List[str] = []

        # PHASE 1: Analyze business
        logger.info("="*60)
        logger.info("🔷 PHASE 1: ANALYZING YOUR BUSINESS")
        logger.info("="*60)
        
        analysis = self.brain.analyze_business(description, products, location)
        logger.info(f"   Industry: {analysis.get('industry', '?')}")
        logger.info(f"   Niche: {analysis.get('niche', '?')}")

        # PHASE 2: Search Facebook
        logger.info("\n" + "="*60)
        logger.info("🔷 PHASE 2: SEARCHING FACEBOOK")
        logger.info("="*60)
        
        queries = self.brain.generate_search_queries(analysis, description, products, location)
        all_queries.extend(queries)
        logger.info(f"   Generated {len(queries)} search queries")

        all_fb_results: List[Dict] = []
        for i, q in enumerate(queries):
            logger.info(f"   🔍 [{i+1}/{len(queries)}] {q[:55]}...")
            results = self.search.search_facebook_pages(q)
            all_fb_results.extend(results)
            time.sleep(0.8)

        # Deduplicate
        unique_results = self._deduplicate_results(all_fb_results)
        logger.info(f"   ✅ Found {len(unique_results)} unique Facebook pages")

        # Classify results
        if unique_results:
            classified = self.brain.classify_search_results(unique_results, analysis)
            self._process_classified_results(classified, unique_results)

        logger.info(f"   ✅ {len(self.competitors)} relevant competitors from search")

        # PHASE 3: LLM recall + search
        logger.info("\n" + "="*60)
        logger.info("🔷 PHASE 3: AI RECALL")
        logger.info("="*60)
        
        recalled = self.brain.recall_competitor_names(analysis, description, products, location)
        logger.info(f"   LLM recalled {len(recalled)} competitor names")

        new_from_recall = self._process_recalled_competitors(recalled, location)
        logger.info(f"   ✅ Found FB pages for {new_from_recall} recalled competitors")

        # PHASE 4: Expansion (if needed)
        for rnd in range(expansion_rounds):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔷 PHASE 4.{rnd+1}: EXPANSION SEARCH")
            logger.info("="*60)
            
            self._expansion_round(all_queries, description, products, location, analysis)

        # PHASE 5: Score & rank
        logger.info("\n" + "="*60)
        logger.info("🔷 PHASE 5: SCORING & RANKING")
        logger.info("="*60)
        
        self._score_and_rank(description, products, location)

        # Summary
        elapsed = time.time() - start
        with_fb = sum(1 for c in self.competitors if c.facebook_url)
        
        logger.info("\n" + "="*60)
        logger.info("🔷 COMPLETE ✅")
        logger.info("="*60)
        logger.info(f"   ⏱️  Time: {elapsed:.0f}s")
        logger.info(f"   🧠 LLM calls: {self.brain.calls}")
        logger.info(f"   🔍 Search calls: {self.search.total_calls}")
        logger.info(f"   📊 Total competitors: {len(self.competitors)}")
        logger.info(f"   📘 With Facebook link: {with_fb}")

        return self.competitors

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on username"""
        unique_results = []
        seen_u = set()
        for r in results:
            u = r.get("_username", "").lower()
            if u and u not in seen_u:
                seen_u.add(u)
                unique_results.append(r)
        return unique_results

    def _process_classified_results(self, classified: List[Dict], unique_results: List[Dict]):
        """Process LLM-classified search results"""
        for item in classified:
            try:
                idx = item.get("index", 0) - 1
                if 0 <= idx < len(unique_results) and item.get("relevant", False):
                    r = unique_results[idx]
                    username = r.get("_username", "")
                    if username and username.lower() not in self._seen_usernames:
                        comp = Competitor(
                            name=item.get("name", r["title"].split("|")[0].strip()),
                            facebook_username=username,
                            facebook_url=f"https://www.facebook.com/{username}",
                            description=r.get("snippet", "")[:200],
                            category=item.get("category", ""),
                            competitor_type=item.get("type", ""),
                            source="search",
                        )
                        self._add(comp)
                        self._seen_usernames.add(username.lower())
            except (IndexError, KeyError):
                continue

    def _process_recalled_competitors(self, recalled: List[Dict], location: str) -> int:
        """Process competitors recalled by LLM and search for their FB pages"""
        new_from_recall = 0
        for item in recalled:
            name = item.get("name", "").strip()
            if not name:
                continue

            # Check if already found
            if self._is_duplicate_name(name):
                continue

            # Search for Facebook page
            logger.info(f"   🔍 Searching FB for: {name}")
            fb_results = self.search.find_page_for_brand(name, location)

            if fb_results:
                r = fb_results[0]
                username = r.get("_username", "")
                if username and username.lower() not in self._seen_usernames:
                    comp = Competitor(
                        name=name,
                        facebook_username=username,
                        facebook_url=f"https://www.facebook.com/{username}",
                        description=r.get("snippet", "")[:200],
                        category=item.get("category", ""),
                        why_competitor=item.get("why", ""),
                        competitor_type=item.get("type", ""),
                        source="llm_recall+search",
                    )
                    self._add(comp)
                    self._seen_usernames.add(username.lower())
                    new_from_recall += 1
                    logger.info(f"      ✅ Found: facebook.com/{username}")
            else:
                # No FB page found — still add as name-only
                comp = Competitor(
                    name=name,
                    category=item.get("category", ""),
                    why_competitor=item.get("why", ""),
                    competitor_type=item.get("type", ""),
                    source="llm_recall",
                )
                self._add(comp)

            time.sleep(0.5)
        
        return new_from_recall

    def _expansion_round(self, all_queries: List[str], desc: str, products: str, loc: str, analysis: Dict):
        """Run one expansion round to find more competitors"""
        # Check if we have any competitors to expand from
        if not self.competitors:
            logger.warning("   ⚠️ No competitors found yet - skipping expansion")
            return
        
        # Generate expansion queries
        logger.info(f"   📋 Generating expansion queries based on {len(self.competitors)} competitors found...")
        exp_queries = self.brain.expansion_queries(self.competitors, all_queries, desc, products, loc)
        
        if not exp_queries:
            logger.warning("   ⚠️ No expansion queries generated - may be LLM issue")
            return
        
        logger.info(f"   ✅ Generated {len(exp_queries)} new queries")
        all_queries.extend(exp_queries)

        new_results = []
        for i, q in enumerate(exp_queries, 1):
            logger.info(f"   🔄 [{i}/{len(exp_queries)}] {q[:55]}...")
            results = self.search.search_facebook_pages(q)
            for r in results:
                u = r.get("_username", "").lower()
                if u and u not in self._seen_usernames:
                    new_results.append(r)
            time.sleep(0.8)

        logger.info(f"   📊 Found {len(new_results)} new Facebook pages from expansion")
        
        if new_results:
            classified = self.brain.classify_search_results(new_results, analysis)
            new_count_before = len(self.competitors)
            self._process_classified_results(classified, new_results)
            new_count_after = len(self.competitors)
            added = new_count_after - new_count_before
            logger.info(f"   ✅ Added {added} new competitors from expansion")
        else:
            logger.info("   ℹ️  No new pages found in this expansion round")

    def _score_and_rank(self, desc: str, products: str, loc: str):
        """Score all competitors and rank them"""
        scores = self.brain.score_all(self.competitors, desc, products, loc)
        for idx, data in scores.items():
            if 0 <= idx < len(self.competitors):
                c = self.competitors[idx]
                c.relevance_score = data.get("score", 0.0)
                if score_type := data.get("type"):
                    c.competitor_type = score_type
                if reason := data.get("reason"):
                    c.why_competitor = reason

        # Sort and filter
        self.competitors.sort(key=lambda c: c.relevance_score, reverse=True)
        self.competitors = [
            c for c in self.competitors
            if c.relevance_score >= 0.25 or c.facebook_url
        ]

    def _is_duplicate_name(self, name: str) -> bool:
        """Check if competitor name already exists"""
        for ex in self.competitors:
            n1 = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF]", "", name.lower())
            n2 = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF]", "", ex.name.lower())
            if n1 and n2 and len(n1) > 2 and (n1 in n2 or n2 in n1):
                return True
        return False

    def _add(self, comp: Competitor) -> bool:
        """Add competitor to list, avoiding duplicates"""
        for ex in self.competitors:
            # Same FB username
            if (comp.facebook_username and ex.facebook_username and
                    comp.facebook_username.lower() == ex.facebook_username.lower()):
                # Merge info
                if comp.description and not ex.description:
                    ex.description = comp.description
                if comp.why_competitor and not ex.why_competitor:
                    ex.why_competitor = comp.why_competitor
                if comp.source not in ex.source:
                    ex.source += f"+{comp.source}"
                return False
            
            # Similar name
            if comp.name and ex.name:
                n1 = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF]", "", comp.name.lower())
                n2 = re.sub(r"[^a-zA-Z0-9\u0600-\u06FF]", "", ex.name.lower())
                if n1 and n2 and len(n1) > 3 and len(n2) > 3 and (n1 in n2 or n2 in n1):
                    if comp.facebook_url and not ex.facebook_url:
                        ex.facebook_url = comp.facebook_url
                        ex.facebook_username = comp.facebook_username
                    if comp.description and not ex.description:
                        ex.description = comp.description
                    if comp.source not in ex.source:
                        ex.source += f"+{comp.source}"
                    return False
        
        self.competitors.append(comp)
        return True

    def get_facebook_usernames(self) -> List[str]:
        """
        Extract list of Facebook usernames for scraping
        
        Returns:
            List of clean Facebook usernames (not full URLs)
        """
        import re
        usernames = []
        for comp in self.competitors:
            username = None
            
            # Try to get from facebook_username field
            if comp.facebook_username:
                username = comp.facebook_username
            # Fallback: extract from facebook_url
            elif comp.facebook_url:
                username = comp.facebook_url
            
            if not username:
                continue
            
            # ROBUST CLEANING - remove ALL URL components
            username = str(username).strip()
            
            # Strip protocol
            username = re.sub(r'^https?://', '', username)
            
            # Strip www.
            username = re.sub(r'^www\.', '', username)
            
            # Strip facebook.com/
            username = re.sub(r'^facebook\.com/', '', username)
            
            # Strip trailing paths (/posts, /about, etc.) - take only first segment
            username = username.split('/')[0]
            
            # Strip query parameters
            username = username.split('?')[0]
            
            # Final cleanup
            username = username.strip()
            
            # Validate - make sure we got a clean username
            if username and 'http' not in username and 'www' not in username and 'facebook.com' not in username:
                if len(username) > 2 and username not in usernames:
                    usernames.append(username)
            else:
                logger.warning(f"   ⚠️ Skipped invalid username: '{username}' from competitor: {comp.name}")
        
        return usernames

    def save_results(self, output_dir: str = ".", prefix: str = "competitors"):
        """Save competitor discovery results"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = os.path.join(output_dir, f"{prefix}_{timestamp}.json")
        
        data = {
            "generated": datetime.now().isoformat(),
            "total": len(self.competitors),
            "with_facebook_link": sum(1 for c in self.competitors if c.facebook_url),
            "competitors": [asdict(c) for c in self.competitors],
        }
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved: {json_file}")
        return json_file
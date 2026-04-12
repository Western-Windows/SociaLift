# we need to replace the llm with transformer for matching
import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI
from competitor_scraper import CompetitorDiscovery, Competitor
from post_scraper import (
    extract_page_from_url,
    worker,
    MAX_PARALLEL_BROWSERS,
    tprint,
)
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ──────────────────────────────────────────────
# COMPETITOR VALIDATOR
# ──────────────────────────────────────────────
class CompetitorValidator:
    """
    Lightweight LLM filter that runs BEFORE scraping.
    Removes pages that are clearly not competitors
    (news sites, event pages, unrelated businesses, etc.)
    """

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model  = model

    def _ask(self, prompt: str) -> str:
        try:
            r = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.0,   # deterministic — this is a yes/no task
            )
            content = r.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            tprint(f"   ⚠️ Validator LLM error: {e}")
            return ""

    def _parse_json(self, text: str):
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            pass
        import re
        m = re.search(r"\[[\s\S]*\]", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return None

    def validate_batch(
        self,
        usernames: List[str],
        competitors: List[Competitor],
        business_description: str,
        products: str,
        chunk_size: int = 30,
    ) -> List[str]:
        """
        Validate a list of Facebook usernames against the business context.
        Returns only the usernames confirmed as real competitors.
        """
        # Build a lookup: username -> competitor name + category
        meta = {}
        for c in competitors:
            u = (c.facebook_username or "").strip().lower()
            if u:
                meta[u] = {
                    "name":     c.name,
                    "category": c.category,
                    "why":      c.why_competitor,
                }

        validated = []
        rejected  = []
        total     = len(usernames)

        for i in range(0, total, chunk_size):
            chunk = usernames[i:i + chunk_size]

            # Build the numbered list with available metadata
            lines = []
            for j, u in enumerate(chunk, 1):
                info = meta.get(u.lower(), {})
                name = info.get("name") or u
                cat  = info.get("category") or "unknown"
                why  = info.get("why") or ""
                line = f'{j}. username="{u}" | name="{name}" | category="{cat}"'
                if why:
                    line += f' | why="{why[:80]}"'
                lines.append(line)

            prompt = f"""You are a competitor validation filter. Be CONSERVATIVE — only reject pages that are CLEARLY NOT competitors.

BUSINESS WE ARE ANALYZING:
- Description: {business_description}
- Products/Services: {products}

RULES:
1. MARK AS VALID (is_competitor: true) if:
   • Same industry/category (e.g. both fashion, both restaurants, both furniture)
   • Sells ANY overlapping product/service, OR could steal the same customer
   • Is a brand, store, reseller, boutique, designer, or marketplace in the same space
   • Even if bigger/smaller, online/offline, luxury/budget — still a competitor

2. MARK AS INVALID (is_competitor: false) ONLY if you are 100% sure:
   • Pure news/media/magazine (e.g. Vogue Egypt, CairoScene)
   • Event/festival (e.g. "Cairo Fashion Week 2024")
   • Service with ZERO product overlap (e.g. architecture firm for a clothing brand)
   • Personal blog/influencer with NO shop/products

3. WHEN IN DOUBT → MARK AS VALID. It is better to keep a maybe-competitor than to delete a real one.

PAGES TO VALIDATE:
{chr(10).join(lines)}

Return a JSON array — one entry per page, in the same order:
[{{"index": 1, "username": "...", "is_competitor": true, "reason": "one sentence", "confidence": "high/medium/low"}}]

Return ONLY valid JSON."""

            raw  = self._ask(prompt)
            data = self._parse_json(raw)

            if not isinstance(data, list):
                # If LLM fails, keep all in this chunk (safe fallback)
                tprint(f"   ⚠️ Validator got no response for chunk {i//chunk_size+1} — keeping all {len(chunk)}")
                validated.extend(chunk)
                continue

            for item in data:
                try:
                    idx = item.get("index", 0) - 1
                    if 0 <= idx < len(chunk):
                        u = chunk[idx]
                        if item.get("is_competitor", True):
                            validated.append(u)
                        else:
                            rejected.append((u, item.get("reason", "")))
                except Exception:
                    pass

            tprint(f"   ✅ Validated chunk {i//chunk_size+1}/{(total-1)//chunk_size+1} "
                   f"— kept {sum(1 for item in data if item.get('is_competitor', True))}, "
                   f"removed {sum(1 for item in data if not item.get('is_competitor', True))}")

        if rejected:
            tprint(f"\n   🗑️  Removed {len(rejected)} non-competitors:")
            for u, reason in rejected[:10]:
                tprint(f"      ✗ {u:<35} {reason}")
            if len(rejected) > 10:
                tprint(f"      ... and {len(rejected)-10} more")

        return validated


class SociaLiftPipeline:
    """
    Main pipeline orchestrator for competitor discovery and post scraping.
    """

    def __init__(
        self,
        openai_api_key: str,
        fb_email: str,
        fb_password: str,
        output_dir: str = "",
    ):
        self.openai_api_key = openai_api_key
        self.fb_email       = fb_email
        self.fb_password    = fb_password
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        self.output_dir     = output_dir

        os.makedirs(output_dir, exist_ok=True)

        self.competitor_discovery = None
        self.validator            = CompetitorValidator(openai_api_key)
        self.competitors:  List[Competitor] = []
        self.post_results: Dict             = {}   # page -> posts_scraped count

    # ─────────────────────────────────────────────────────────────────
    def run(
        self,
        business_description: str,
        products: str,
        location: str,
        days_to_scrape: int = 10,
        expansion_rounds: int = 2,
        max_competitors_to_scrape: Optional[int] = None,
    ) -> Dict:
        tprint("\n" + "="*70)
        tprint("  🚀 SOCIALIFT PIPELINE - STARTING")
        tprint("="*70)

        start_time = time.time()

        # ═════════════════════════════════════════════════════════════
        # STAGE 1: DISCOVER COMPETITORS
        # ═════════════════════════════════════════════════════════════
        tprint("\n" + "█"*70)
        tprint("  STAGE 1: COMPETITOR DISCOVERY")
        tprint("█"*70)

        try:
            self.competitor_discovery = CompetitorDiscovery(
                openai_key=self.openai_api_key,
                model="gpt-4o-mini",
            )

            self.competitors = self.competitor_discovery.discover(
                description=business_description,
                products=products,
                location=location,
                expansion_rounds=expansion_rounds,
            )

            comp_file = self.competitor_discovery.save_results(
                output_dir=self.output_dir,
                prefix="competitors",
            )

            tprint(f"\n✅ STAGE 1 COMPLETE")
            tprint(f"   Found {len(self.competitors)} competitors")
            tprint(f"   Saved to: {comp_file}")

        except Exception as e:
            tprint(f"\n❌ STAGE 1 FAILED: {e}")
            raise

        # ═════════════════════════════════════════════════════════════
        # STAGE 2: PREPARE FOR SCRAPING
        # ═════════════════════════════════════════════════════════════
        tprint("\n" + "█"*70)
        tprint("  STAGE 2: PREPARING POST SCRAPER")
        tprint("█"*70)

        fb_usernames      = []
        missing_usernames = []
        for comp in self.competitor_discovery.competitors:
            if getattr(comp, 'facebook_username', None):
                fb_usernames.append(comp.facebook_username.strip())
            else:
                missing_usernames.append(getattr(comp, 'name', 'UNKNOWN'))

        if missing_usernames:
            tprint(f"\n⚠️  WARNING: {len(missing_usernames)} competitors missing "
                   f"facebook_username: {missing_usernames[:3]}")

        if not fb_usernames:
            tprint("\n⚠️  No Facebook usernames found! Skipping post scraping.")
            return self._generate_summary(start_time)

        tprint(f"\n   Found {len(fb_usernames)} Facebook usernames to scrape")

        if max_competitors_to_scrape and max_competitors_to_scrape < len(fb_usernames):
            fb_usernames = fb_usernames[:max_competitors_to_scrape]
            tprint(f"   Limited to {len(fb_usernames)} usernames "
                   f"(max_competitors_to_scrape={max_competitors_to_scrape})")

        tprint(f"\n   Pages to scrape:")
        for i, u in enumerate(fb_usernames[:10], 1):
            tprint(f"   {i}. {u}")
        if len(fb_usernames) > 10:
            tprint(f"   ... and {len(fb_usernames) - 10} more")

        # ═════════════════════════════════════════════════════════════
        # STAGE 2.5: VALIDATE COMPETITORS  (filter before scraping)
        # ═════════════════════════════════════════════════════════════
        tprint("\n" + "█"*70)
        tprint("  STAGE 2.5: VALIDATING COMPETITORS")
        tprint("█"*70)
        tprint(f"\n   Running LLM validation on {len(fb_usernames)} pages...")

        before = len(fb_usernames)
        fb_usernames = self.validator.validate_batch(
            usernames=fb_usernames,
            competitors=self.competitor_discovery.competitors,
            business_description=business_description,
            products=products,
        )
        after = len(fb_usernames)

        tprint(f"\n✅ STAGE 2.5 COMPLETE")
        tprint(f"   Kept:    {after} confirmed competitors")
        tprint(f"   Removed: {before - after} non-competitors")
        tprint(f"   Time saved: ~{(before - after) * 40 // 60} min (est. {before - after} browser sessions skipped)")

        if not fb_usernames:
            tprint("\n⚠️  No valid competitors remaining after validation!")
            return self._generate_summary(start_time)

        # ═════════════════════════════════════════════════════════════
        # STAGE 3: SCRAPE POSTS  (parallel browsers, one per thread)
        # ═════════════════════════════════════════════════════════════
        tprint("\n" + "█"*70)
        tprint("  STAGE 3: SCRAPING COMPETITOR POSTS")
        tprint("█"*70)

        parallel = min(MAX_PARALLEL_BROWSERS, len(fb_usernames))
        tprint(f"\n🚀 Launching up to {parallel} browsers in parallel...\n")

        scrape_results = []
        try:
            with ThreadPoolExecutor(max_workers=parallel) as pool:
                futures = {
                    pool.submit(worker, page, days_to_scrape, tid): page
                    for tid, page in enumerate(fb_usernames, 1)
                }
                for future in as_completed(futures):
                    page = futures[future]
                    try:
                        result = future.result()
                        scrape_results.append(result)
                        self.post_results[result["page"]] = result["posts_scraped"]
                    except Exception as e:
                        tprint(f"❌ Future for '{page}' raised: {e}")
                        scrape_results.append({
                            "page": page,
                            "status": f"❌ Error: {e}",
                            "posts_scraped": 0,
                        })

            total_posts = sum(r["posts_scraped"] for r in scrape_results)
            tprint(f"\n✅ STAGE 3 COMPLETE")
            tprint(f"   Scraped {len(scrape_results)} pages")
            tprint(f"   Total posts: {total_posts}")

        except Exception as e:
            tprint(f"\n❌ STAGE 3 FAILED: {e}")

        # ═════════════════════════════════════════════════════════════
        # STAGE 4: FINAL SUMMARY
        # ═════════════════════════════════════════════════════════════
        return self._generate_summary(start_time, scrape_results)

    # ─────────────────────────────────────────────────────────────────
    def _generate_summary(self, start_time: float, scrape_results:Optional [list] = None) -> Dict:
        elapsed          = time.time() - start_time
        scrape_results   = scrape_results or []
        total_posts      = sum(r["posts_scraped"] for r in scrape_results)
        pages_with_posts = sum(1 for r in scrape_results if r["posts_scraped"] > 0)

        summary = {
            "pipeline_completed":   True,
            "elapsed_time_seconds": round(elapsed, 2),
            "timestamp":            datetime.now().isoformat(),
            "competitors": {
                "total_found":         len(self.competitors),
                "with_facebook_pages": sum(1 for c in self.competitors if getattr(c, 'facebook_url', None)),
                "scraped":             len(scrape_results),
            },
            "posts": {
                "total_scraped":    total_posts,
                "pages_with_posts": pages_with_posts,
                "average_per_page": round(total_posts / max(len(scrape_results), 1), 1),
            },
            "output_directory": self.output_dir,
        }

        summary_file = os.path.join(
            self.output_dir,
            f"pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        tprint("\n" + "="*70)
        tprint("  🎉 PIPELINE COMPLETE!")
        tprint("="*70)
        tprint(f"\n  ⏱️  Total time: {elapsed/60:.1f} minutes")
        tprint(f"\n  📊 COMPETITORS:")
        tprint(f"     • Total found:          {summary['competitors']['total_found']}")
        tprint(f"     • With Facebook pages:  {summary['competitors']['with_facebook_pages']}")
        tprint(f"     • Successfully scraped: {summary['competitors']['scraped']}")
        tprint(f"\n  📄 POSTS:")
        tprint(f"     • Total posts scraped:  {summary['posts']['total_scraped']}")
        tprint(f"     • Pages with posts:     {summary['posts']['pages_with_posts']}")
        tprint(f"     • Average per page:     {summary['posts']['average_per_page']}")
        tprint(f"\n  💾 All results saved to: {self.output_dir}")
        tprint(f"     📋 Summary: {summary_file}")
        tprint("="*70)

        # Per-page breakdown
        if scrape_results:
            tprint(f"\n{'='*60}")
            tprint("📊  SCRAPING SUMMARY")
            tprint(f"{'='*60}")
            for r in sorted(scrape_results, key=lambda x: x["page"]):
                tprint(f"  {r['status']:<20}  {r['page']:<30}  {r['posts_scraped']} posts")
            tprint(f"{'='*60}")

        return summary


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              SOCIALIFT PIPELINE - FULL WORKFLOW               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1️⃣  Discover competitors using AI + web search              ║
║  2️⃣  Find their Facebook pages                               ║
║  3️⃣  Scrape posts (parallel browsers, no shared login)       ║
║  4️⃣  Generate comprehensive reports                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    openai_key  = os.environ.get("OPENAI_API_KEY", "") or input("\n🔑 OpenAI API key: ").strip()
    fb_email    = "fcisblah@gmail.com"
    fb_password = "Fcis12345678!"
    output_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

    print(f"\n{'─'*60}")
    print("Tell me about your business:\n")

    business_description = input("📝 Business description:\n   > ").strip()
    products             = input("\n🛍️  Products/services:\n   > ").strip()
    location             = input("\n📍 Location:\n   > ").strip()

    if not business_description:
        business_description = "Ergonomic desk accessories brand"
        products             = "laptop stands, desk organizers, ergonomic accessories"
        location             = "Cairo, Egypt"
        print(f"\n   Using defaults: {business_description}")

    days_to_scrape  = 10
    max_competitors = None
    print(f"\n📅 Will scrape last {days_to_scrape} days of posts")

    pipeline = SociaLiftPipeline(
        openai_api_key=openai_key,
        fb_email=fb_email,
        fb_password=fb_password,
        output_dir=output_dir,
    )

    try:
        pipeline.run(
            business_description=business_description,
            products=products,
            location=location,
            days_to_scrape=days_to_scrape,
            expansion_rounds=1,
            max_competitors_to_scrape=max_competitors,
        )
        print("\n✅ Pipeline completed successfully!")
        print("\n📂 Check your output directory for all results.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
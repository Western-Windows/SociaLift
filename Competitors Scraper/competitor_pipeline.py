# we need to replace the llm with transformer for matching
import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

# Import our refactored modules
from competitor_scraper import CompetitorDiscovery, Competitor
from post_scraper import (
    FacebookGraphqlScraper,
    perform_login,
    process_posts_batch,
    save_results as save_post_results
)


class SociaLiftPipeline:
    """
    Main pipeline orchestrator for competitor discovery and post scraping
    """
    
    def __init__(self, openai_api_key: str, fb_email: str, fb_password: str, output_dir: str = "d:/Graduation Project/SociaLift"):
        """
        Initialize the pipeline
        
        Args:
            openai_api_key: OpenAI API key for competitor discovery
            fb_email: Facebook login email
            fb_password: Facebook login password
            output_dir: Directory to save all results
        """
        self.openai_api_key = openai_api_key
        self.fb_email = fb_email
        self.fb_password = fb_password
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.competitor_discovery = None
        self.fb_scraper = None
        self.competitors: List[Competitor] = []
        self.post_results: Dict = {}
        
    def run(self, business_description: str, products: str, location: str, 
            days_to_scrape: int = 10, expansion_rounds: int = 2,
            max_competitors_to_scrape: Optional[int] = None):
        """
        Run the complete pipeline
        
        Args:
            business_description: Your business description
            products: Products/services you offer
            location: Your business location
            days_to_scrape: Number of days of posts to scrape per competitor
            expansion_rounds: Number of search expansion rounds
            max_competitors_to_scrape: Maximum number of competitors to scrape (None = all)
        
        Returns:
            Dictionary with competitors and post results
        """
        print("\n" + "="*70)
        print("  🚀 SOCIALIFT PIPELINE - STARTING")
        print("="*70)
        
        start_time = time.time()
        
        # ═════════════════════════════════════════════════════════════════
        # STAGE 1: DISCOVER COMPETITORS
        # ═════════════════════════════════════════════════════════════════
        print("\n" + "█"*70)
        print("  STAGE 1: COMPETITOR DISCOVERY")
        print("█"*70)
        
        try:
            self.competitor_discovery = CompetitorDiscovery(
                openai_key=self.openai_api_key,
                model="gpt-4o-mini"
            )
            
            self.competitors = self.competitor_discovery.discover(
                description=business_description,
                products=products,
                location=location,
                expansion_rounds=expansion_rounds
            )
            
            # Save competitor results
            comp_file = self.competitor_discovery.save_results(
                output_dir=self.output_dir,
                prefix="competitors"
            )
            
            print(f"\n✅ STAGE 1 COMPLETE")
            print(f"   Found {len(self.competitors)} competitors")
            print(f"   Saved to: {comp_file}")
            
        except Exception as e:
            print(f"\n❌ STAGE 1 FAILED: {e}")
            raise
        
        # ═════════════════════════════════════════════════════════════════
        # STAGE 2: PREPARE FOR SCRAPING
        # ═════════════════════════════════════════════════════════════════
        print("\n" + "█"*70)
        print("  STAGE 2: PREPARING POST SCRAPER")
        print("█"*70)
        
        # Get Facebook usernames ONLY from facebook_username field
        fb_usernames = []
        missing_usernames = []
        for comp in self.competitor_discovery.competitors:
            if getattr(comp, 'facebook_username', None):
                fb_usernames.append(comp.facebook_username.strip())
            else:
                missing_usernames.append(getattr(comp, 'name', 'UNKNOWN'))
        if missing_usernames:
            print(f"\n⚠️  WARNING: {len(missing_usernames)} competitors missing facebook_username: {missing_usernames[:3]}")
        if not fb_usernames:
            print("\n⚠️  No Facebook usernames found! Skipping post scraping.")
            return self._generate_summary(start_time)
        print(f"\n   Found {len(fb_usernames)} Facebook usernames to scrape")
        # Limit if requested
        if max_competitors_to_scrape and max_competitors_to_scrape < len(fb_usernames):
            fb_usernames = fb_usernames[:max_competitors_to_scrape]
            print(f"   Limited to {len(fb_usernames)} usernames (max_competitors_to_scrape={max_competitors_to_scrape})")
        
        # Display pages to scrape
        print(f"\n   Pages to scrape:")
        for i, username in enumerate(fb_usernames[:10], 1):
            print(f"   {i}. {username}")
        if len(fb_usernames) > 10:
            print(f"   ... and {len(fb_usernames) - 10} more")
        
        # Validate usernames (catch URL issues early)
        invalid_usernames = [u for u in fb_usernames if 'http' in u or 'www' in u]
        if invalid_usernames:
            print(f"\n   ⚠️  WARNING: Found {len(invalid_usernames)} invalid usernames (contain http/www)")
            print(f"   First few: {invalid_usernames[:3]}")
            print(f"   Attempting to clean them automatically...")
        
        # ═════════════════════════════════════════════════════════════════
        # STAGE 3: LOGIN TO FACEBOOK (ONCE)
        # ═════════════════════════════════════════════════════════════════
        print("\n" + "█"*70)
        print("  STAGE 3: FACEBOOK LOGIN")
        print("█"*70)
        
        try:
            # Initialize scraper
            self.fb_scraper = FacebookGraphqlScraper(
                driver_path="",
                open_browser=True
            )
            
            # Perform login ONCE
            login_success = perform_login(
                self.fb_scraper.page_optional.driver,
                self.fb_email,
                self.fb_password
            )
            
            if not login_success:
                raise Exception("Facebook login failed")
            
            # Mark as logged in
            self.fb_scraper.fb_account = "manual_login"
            self.fb_scraper.page_optional.fb_account = "manual_login"
            
            print(f"\n✅ STAGE 3 COMPLETE - Logged in as {self.fb_email}")
            
        except Exception as e:
            print(f"\n❌ STAGE 3 FAILED: {e}")
            self._cleanup_scraper()
            raise
        
        # ═════════════════════════════════════════════════════════════════
        # STAGE 4: SCRAPE POSTS FROM ALL COMPETITORS
        # ═════════════════════════════════════════════════════════════════
        print("\n" + "█"*70)
        print("  STAGE 4: SCRAPING COMPETITOR POSTS")
        print("█"*70)
        
        try:
            # Scrape all pages in batch (reusing login session)
            self.post_results = process_posts_batch(
                scraper=self.fb_scraper,
                page_usernames=fb_usernames,
                days_back=days_to_scrape,
                output_dir=self.output_dir
            )
            
            # Save post results
            post_files = save_post_results(
                self.post_results,
                output_dir=self.output_dir
            )
            
            total_posts = sum(len(posts) for posts in self.post_results.values())
            
            print(f"\n✅ STAGE 4 COMPLETE")
            print(f"   Scraped {len(self.post_results)} pages")
            print(f"   Total posts: {total_posts}")
            print(f"   Saved {len(post_files)} files")
            
        except Exception as e:
            print(f"\n❌ STAGE 4 FAILED: {e}")
        finally:
            # Always cleanup browser
            self._cleanup_scraper()
        
        # ═════════════════════════════════════════════════════════════════
        # STAGE 5: GENERATE FINAL SUMMARY
        # ═════════════════════════════════════════════════════════════════
        return self._generate_summary(start_time)
    
    def _cleanup_scraper(self):
        """Cleanup Facebook scraper browser"""
        if self.fb_scraper:
            try:
                self.fb_scraper.page_optional.quit_driver()
                print("\n   🔒 Browser closed")
            except:
                pass
    
    def _generate_summary(self, start_time: float) -> Dict:
        """Generate final pipeline summary"""
        elapsed = time.time() - start_time
        
        total_posts = sum(len(posts) for posts in self.post_results.values())
        pages_with_posts = sum(1 for posts in self.post_results.values() if posts)
        
        summary = {
            "pipeline_completed": True,
            "elapsed_time_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
            "business_analyzed": True,
            "competitors": {
                "total_found": len(self.competitors),
                "with_facebook_pages": sum(1 for c in self.competitors if c.facebook_url),
                "scraped": len(self.post_results),
            },
            "posts": {
                "total_scraped": total_posts,
                "pages_with_posts": pages_with_posts,
                "average_per_page": round(total_posts / max(len(self.post_results), 1), 1),
            },
            "output_directory": self.output_dir,
        }
        
        # Save summary
        summary_file = os.path.join(self.output_dir, f"pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        # Print final report
        print("\n" + "="*70)
        print("  🎉 PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n  ⏱️  Total time: {elapsed/60:.1f} minutes")
        print(f"\n  📊 COMPETITORS:")
        print(f"     • Total found: {summary['competitors']['total_found']}")
        print(f"     • With Facebook pages: {summary['competitors']['with_facebook_pages']}")
        print(f"     • Successfully scraped: {summary['competitors']['scraped']}")
        print(f"\n  📄 POSTS:")
        print(f"     • Total posts scraped: {summary['posts']['total_scraped']}")
        print(f"     • Pages with posts: {summary['posts']['pages_with_posts']}")
        print(f"     • Average per page: {summary['posts']['average_per_page']}")
        print(f"\n  💾 All results saved to: {self.output_dir}")
        print(f"     📋 Summary: {summary_file}")
        print("="*70)
        
        return summary


def main():
    """Main entry point for the pipeline"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              SOCIALIFT PIPELINE - FULL WORKFLOW               ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  1️⃣  Discover competitors using AI + web search              ║
║  2️⃣  Find their Facebook pages                               ║
║  3️⃣  Login to Facebook (ONCE)                                ║
║  4️⃣  Scrape posts from all competitors                       ║
║  5️⃣  Generate comprehensive reports                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # ─────────────────────────────────────────────────────────────────
    # CONFIGURATION
    # ─────────────────────────────────────────────────────────────────
    
    # OpenAI API Key
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        # Hardcoded for now (you can change this)
        openai_key = ""
    
    if not openai_key:
        openai_key = input("\n🔑 OpenAI API key: ").strip()
    
    # Facebook credentials
    fb_email = "fcisblah@gmail.com"
    fb_password = "Fcis12345678!"
    
    # Output directory
    output_dir = "d:/Graduation Project/SociaLift"
    
    # ─────────────────────────────────────────────────────────────────
    # BUSINESS INFORMATION
    # ─────────────────────────────────────────────────────────────────
    
    print(f"\n{'─'*60}")
    print("Tell me about your business:\n")
    
    business_description = input("📝 Business description:\n   > ").strip()
    products = input("\n🛍️  Products/services:\n   > ").strip()
    location = input("\n📍 Location:\n   > ").strip()
    
    # Defaults for testing
    if not business_description:
        business_description = "Ergonomic desk accessories brand"
        products = "laptop stands, desk organizers, ergonomic accessories"
        location = "Cairo, Egypt"
        print(f"\n   Using defaults: {business_description}")
    
    # Scraping parameters
    days_to_scrape = 10
    print(f"\n📅 Will scrape last {days_to_scrape} days of posts")
    
    # Optional: limit number of competitors to scrape
    max_competitors = None  # Set to a number like 5 to limit, or None for all
    
    # ─────────────────────────────────────────────────────────────────
    # RUN PIPELINE
    # ─────────────────────────────────────────────────────────────────
    
    pipeline = SociaLiftPipeline(
        openai_api_key=openai_key,
        fb_email=fb_email,
        fb_password=fb_password,
        output_dir=output_dir
    )
    
    try:
        results = pipeline.run(
            business_description=business_description,
            products=products,
            location=location,
            days_to_scrape=days_to_scrape,
            expansion_rounds=1,
            max_competitors_to_scrape=max_competitors
        )
        
        print("\n✅ Pipeline completed successfully!")
        print("\n📂 Check your output directory for all results.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        pipeline._cleanup_scraper()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        pipeline._cleanup_scraper()
        sys.exit(1)


if __name__ == "__main__":
    main()
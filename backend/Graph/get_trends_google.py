#!/usr/bin/env python3

import requests
import json
import logging
import sys
import time
import random
import warnings
from datetime import datetime
from pytrends.request import TrendReq

# Attempt to import filter logic; if it fails, we'll define a dummy or skip
try:
    from filter_trends import filter_trends_with_ai
except ImportError:
    def filter_trends_with_ai():
        print("⚠️ filter_trends.py not found. Skipping AI filtering.")

warnings.simplefilter(action='ignore', category=FutureWarning)

try:
    from config import Config
except ImportError:
    print("Error: config.py not found. Please ensure FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID are set.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Refined Seed Terms for better hit rates
SEED_TERMS = [
    "Technology", "Real Estate", "Food", "Fashion", "Sports", 
    "Business", "Marketing", "Education", "Health", "E-commerce"
]

COUNTRY_MAP = {
    "egypt": "EG", "united states": "US", "united kingdom": "GB",
    "saudi arabia": "SA", "uae": "AE", "germany": "DE", "france": "FR"
}

class ContentManager:
    def __init__(self, country="egypt"):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.country_name = country.lower()
        self.geo_code = COUNTRY_MAP.get(self.country_name, "EG")

        # Increased timeout and added proxies if you have them
        self.pytrends = TrendReq(
            hl="en-US",
            tz=-120,
            timeout=(15, 30),
            retries=3,
            backoff_factor=1
        )

    def fetch_trends(self):
        all_trends = {}
        print(f"📡 Connecting to Google Trends for {self.country_name.upper()}...")

        for seed in SEED_TERMS:
            try:
                # Crucial: Longer, randomized sleep to prevent 429 errors
                sleep_time = random.uniform(5, 10)
                print(f"🔍 Checking: '{seed}' (Waiting {sleep_time:.1f}s...)")
                time.sleep(sleep_time)

                self.pytrends.build_payload(
                    [seed],
                    timeframe="now 7-d",
                    geo=self.geo_code
                )

                related = self.pytrends.related_queries()
                
                if related and seed in related:
                    rising = related[seed].get("rising")
                    
                    if rising is not None and not rising.empty:
                        print(f"   ✅ Found {len(rising)} rising topics for '{seed}'")
                        for _, row in rising.iterrows():
                            keyword = row["query"]
                            score = row["value"]
                            # Weighting: Breakout trends (score=None or very high) get 1000
                            numeric_score = 1000 if str(score).lower() == 'breakout' else int(score)
                            all_trends[keyword] = all_trends.get(keyword, 0) + numeric_score
                    else:
                        print(f"   ℹ️ No rising data for '{seed}'")
                
            except Exception as e:
                print(f"   ❌ Error fetching '{seed}': {e}")
                # If we hit a 429, we should stop or wait much longer
                if "429" in str(e):
                    print("🛑 Rate limit hit (429). Cooling down for 60s...")
                    time.sleep(60)
                continue

        # Sort and take top 50
        sorted_trends = sorted(all_trends.items(), key=lambda x: x[1], reverse=True)[:50]
        return [{"topic": k, "score": v} for k, v in sorted_trends]

    def get_detailed_events(self):
        try:
            url = f"{self.base_url}/{self.page_id}/events"
            params = {"access_token": self.token, "fields": "name,start_time", "limit": 10}
            r = requests.get(url, params=params, timeout=10)
            return r.json().get("data", [])
        except Exception:
            return []

    def save(self, data):
        import os
        path = "./Graph API/JSON"
        if not os.path.exists(path):
            os.makedirs(path)
            
        file_path = f"{path}/top_trends.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {file_path}")

def main(country="egypt"):
    print("\n" + "=" * 50)
    print("🚀 SOCIALIFT: TREND SCANNER v1.1")
    print("=" * 50)

    manager = ContentManager(country)
    trends = manager.fetch_trends()

    if not trends:
        print("\n⚠️ No trends found. Check your internet connection or Google rate limits.")
        return

    output = {
        "meta": {
            "country": country,
            "region_code": manager.geo_code,
            "generated_at": datetime.now().isoformat(),
            "total_found": len(trends)
        },
        "top_50_trends": trends,
        "page_events": manager.get_detailed_events()
    }

    print(f"\n✨ Successfully captured {len(trends)} trending topics.")
    manager.save(output)
    
    print("🤖 Passing data to AI Filter...")
    filter_trends_with_ai()

if __name__ == "__main__":
    # You can change this to any country in COUNTRY_MAP
    main(country="egypt")
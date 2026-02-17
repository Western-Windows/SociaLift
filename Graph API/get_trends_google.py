#!/usr/bin/env python3
"""
Clean Country-Based Trend Fetcher (Safe Mode)

Changes:
1. Country is a parameter (default = Egypt).
2. Category filtering REMOVED.
3. Returns TOP 50 trending topics.
4. Keeps original PyTrends scraping logic intact.
"""

import requests
import json
import logging
import sys
import time
import random
import warnings
from datetime import datetime
from pytrends.request import TrendReq
from filter_trends import filter_trends_with_ai

warnings.simplefilter(action='ignore', category=FutureWarning)

try:
    from config import Config
except ImportError:
    print("Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# 🔑 Neutral seeds (category-free)
SEED_TERMS = [
    # 1. Local Business & Services
    "Advertising/Marketing Service",
    "Agriculture",
    "Automotive",
    "Beauty, Cosmetic & Personal Care",
    "Commercial & Industrial",
    "Education",
    "Event Planning/Event Services",
    "Finance",
    "Food & Beverage",
    "Hotel & Lodging",
    "Legal",
    "Medical & Health",
    "Real Estate",
    "Shopping & Retail",
    "Travel & Transportation",

    # 2. Arts, Culture & Entertainment
    "Art",
    "Book & Magazine",
    "Concert Tour / Event",
    "Library",
    "Media/News Company",
    "Movie / Movie Character",
    "Music",
    "Radio Station",
    "Sports Venue / Stadium",
    "TV Channel / TV Show",

    # 3. People & Public Figures
    "Actor/Director",
    "Artist",
    "Athlete",
    "Author",
    "Blogger",
    "Business Person / Entrepreneur",
    "Chef",
    "Coach",
    "Comedian",
    "Designer",
    "Doctor",
    "Gamer",
    "Journalist",
    "Musician/Band",
    "Photographer",
    "Politician",
    "Public Figure",
    "Teacher",
    "Video Creator",
    "Writer",

    # 4. Brands & Products
    "App Page",
    "Appliances",
    "Baby Goods/Kids Goods",
    "Cars",
    "Clothing",
    "Computers / Electronics",
    "Food/Beverages",
    "Furniture",
    "Games/Toys",
    "Health/Beauty",
    "Home Decor",
    "Jewelry/Watches",
    "Kitchen/Cooking",
    "Pet Supplies",
    "Phone/Tablet",
    "Software",
    "Tools/Equipment",
    "Video Game",
    "Vitamins/Supplements",
    "Website",

    # 5. Communities & Non-Profits
    "Cause",
    "Community Organization",
    "Environmental Conservation",
    "Government Organization",
    "Non-Governmental Organization (NGO)",
    "Non-Profit Organization",
    "Political Organization",
    "Religious Organization"
]

# 🌍 Country map
COUNTRY_MAP = {
    "egypt": "EG",
    "united states": "US",
    "united kingdom": "GB",
    "saudi arabia": "SA",
    "uae": "AE",
    "germany": "DE",
    "france": "FR"
}

class ContentManager:
    def __init__(self, country="egypt"):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID

        self.country_name = country.lower()
        self.geo_code = COUNTRY_MAP.get(self.country_name, "EG")

        self.pytrends = TrendReq(
            hl="en-US",
            tz=-120,
            timeout=(10, 25),
            retries=2,
            backoff_factor=1
        )

    # ==========================
    # 🌍 TREND SCRAPER (UNCHANGED LOGIC)
    # ==========================
    def fetch_trends(self):
        all_trends = {}

        for seed in SEED_TERMS:
            try:
                time.sleep(random.uniform(2, 4))

                self.pytrends.build_payload(
                    [seed],
                    timeframe="now 7-d",
                    geo=self.geo_code
                )

                related = self.pytrends.related_queries()
                if not related or seed not in related:
                    continue

                rising = related[seed]["rising"]
                if rising is None or rising.empty:
                    continue

                for _, row in rising.iterrows():
                    keyword = row["query"]
                    score = row["value"]
                    all_trends[keyword] = all_trends.get(keyword, 0) + score

            except Exception:
                continue

        # 🔝 keep top 50
        sorted_trends = sorted(
            all_trends.items(),
            key=lambda x: x[1],
            reverse=True
        )[:50]

        # ✅ OLD JSON FORMAT PRESERVED
        return [
            {
                "topic": keyword,
                "score": score
            }
            for keyword, score in sorted_trends
        ]

        # ==========================
        # 📅 FACEBOOK EVENTS (UNCHANGED)
        # ==========================
    def get_detailed_events(self):
        try:
            url = f"{self.base_url}/{self.page_id}/events"
            params = {
                "access_token": self.token,
                "fields": "name,start_time",
                "limit": 20
            }
            r = requests.get(url, params=params, timeout=10)
            return r.json().get("data", [])
        except:
            return []

    def save(self, data):
        with open("top_trends.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("\n💾 Saved to top_trends.json")

# ==========================
# 🚀 MAIN
# ==========================
def main(country="egypt"):
    print("\n" + "=" * 50)
    print("   COUNTRY-BASED TREND SCANNER")
    print("=" * 50)

    manager = ContentManager(country)

    print(f"\n🌍 Country: {country.title()} ({manager.geo_code})")
    print("🔍 Fetching trends...\n")

    trends = manager.fetch_trends()

    output = {
        "meta": {
            "country": country,
            "region_code": manager.geo_code,
            "generated_at": datetime.now().isoformat()
        },
        "top_50_trends": trends,
        "page_events": manager.get_detailed_events()
    }

    print(f"✅ Found {len(trends)} trending topics.")
    manager.save(output)
    filter_trends_with_ai()

if __name__ == "__main__":
   main(country="egypt")
   

#!/usr/bin/env python3

"""
Filename: get_holidays.py
Version: 1.0
Description:
This script is designed to fetch upcoming public holidays and regional trends.
It uses the page location to determine the region with default region as Egypt.
"""

import requests
import json
import logging
import sys
import datetime
import holidays
import warnings
from pytrends.request import TrendReq
import pandas as pd
warnings.simplefilter(action='ignore', category=FutureWarning)

try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class RegionalManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.pytrends = TrendReq(hl='en-US', tz=360)

        self.iso_map = {
            "Egypt": "EG", "United States": "US", "United Kingdom": "GB",
            "Canada": "CA", "Australia": "AU", "Germany": "DE", 
            "France": "FR", "India": "IN", "Saudi Arabia": "SA",
            "United Arab Emirates": "AE", "Brazil": "BR"
        }

        self.trends_map = {
            "EG": "egypt", "US": "united_states", "GB": "united_kingdom",
            "CA": "canada", "AU": "australia", "DE": "germany",
            "FR": "france", "IN": "india", "SA": "saudi_arabia",
            "AE": "united_arab_emirates", "BR": "brazil"
        }

    def get_page_region(self):
        """
        Determines the region code (ISO) to use.
        Prioritizes Page Location -> Defaults to Egypt (EG).
        """
        url = f"{self.base_url}/{self.page_id}"
        params = {"access_token": self.token, "fields": "location,name"}
        
        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            page_name = data.get('name', 'Unknown Page')
            country_name = data.get('location', {}).get('country')

            if country_name and country_name in self.iso_map:
                return page_name, self.iso_map[country_name], country_name, "PAGE_LOCATION"

            return page_name, "EG", "Egypt", "DEFAULT"

        except Exception:
            return "Unknown Page", "EG", "Egypt", "DEFAULT (Error)"

    def get_upcoming_holidays(self, iso_code):
        """
        Fetches official public holidays for the given country code.
        Returns holidays occurring in the next 60 days.
        """
        try:

            year = datetime.date.today().year
            country_holidays = holidays.country_holidays(iso_code, years=year)
            upcoming = []
            today = datetime.date.today()
            limit_date = today + datetime.timedelta(days=60)

            for date, name in sorted(country_holidays.items()):
                if today <= date <= limit_date:
                    days_until = (date - today).days

                    advice = "Plan content."
                    if days_until == 0: advice = "Post 'Happy Holiday' message NOW."
                    elif days_until < 3: advice = "Post last-minute preparation tips."
                    elif days_until < 7: advice = "Start hype/countdown."

                    upcoming.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "holiday_name": name,
                        "days_until": days_until,
                        "content_advice": advice
                    })
            
            return upcoming

        except Exception as e:
            logger.error(f"Holiday Fetch Error: {e}")
            return []

    def get_regional_trends(self, iso_code):
        """
        Fetches 'Trending Searches' from Google for that specific country.
        """
        trend_location = self.trends_map.get(iso_code, 'egypt') 
        
        try:
            df = self.pytrends.trending_searches(pn=trend_location)
            trends = df.head(10).values.flatten().tolist()
            rich_trends = []
            for t in trends:
                rich_trends.append({
                    "keyword": t,
                    "google_search_link": f"https://www.google.com/search?q={t.replace(' ', '+')}",
                    "type": "Daily Search Trend"
                })
            return rich_trends

        except Exception as e:
            logger.error(f"Trends Error: {e}")
            return []

    def save_to_json(self, data, filename="./Graph API/JSON/regional_events_holidays.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n   💾 Data saved to: {filename}")
        except Exception:
            pass

def main():
    print("\n" + "="*50)
    print("   🌍 REGIONAL EVENTS & HOLIDAYS FETCHER")
    print("="*50)

    manager = RegionalManager()
    print("\n   [1/3] Detecting Region...")
    page_name, iso_code, country_name, source = manager.get_page_region()
    
    print(f"      Page: {page_name}")
    print(f"      📍 Active Region: {country_name} ({iso_code})")
    print(f"      ℹ️  Source: {source}")
    print(f"\n   [2/3] Fetching Upcoming Holidays for {country_name}...")
    holidays_list = manager.get_upcoming_holidays(iso_code)
    
    if holidays_list:
        print(f"      🎉 Found {len(holidays_list)} upcoming holidays.")
        for h in holidays_list:
            print(f"         - {h['date']}: {h['holiday_name']} (in {h['days_until']} days)")
    else:
        print("      ℹ️  No public holidays in the next 60 days.")

    output = {
        "meta": {
            "page": page_name,
            "region": country_name,
            "region_code": iso_code,
            "generated_at": datetime.datetime.now().isoformat()
        },
        "upcoming_holidays": holidays_list,
    }
    
    manager.save_to_json(output)

if __name__ == "__main__":
    main()
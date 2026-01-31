#!/usr/bin/env python3
"""
Facebook Comprehensive Page Info Fetcher
Features:
1. Fetches ALL basic fields requested (ID, stats, contact, location).
2. Adds extra available fields (Bio, WhatsApp, Mission, Founded, etc.).
3. Groups output logically in the console.
4. Saves raw data to JSON.
"""

import requests
import json
import logging
import sys
from datetime import datetime

# Try to import config
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class PageInfoManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
    
    def get_full_page_details(self):
        """
        Fetches a massive list of fields to get every available detail.
        """
        print(f"   🔍 Fetching comprehensive details for Page ID: {self.page_id}...")

        # 1. Your Requested Fields + 2. Additional Useful Fields
        fields_list = [
            # --- Basic Identity ---
            'id', 'name', 'username', 'about', 'bio', 'description', 
            'category', 'category_list', 'verification_status', 'is_published',
            
            # --- Links & Contact ---
            'link', 'website', 'emails', 'phone', 'whatsapp_number',
            
            # --- Location & Hours ---
            'location', 'hours', 'is_always_open', 'is_permanently_closed',
            
            # --- Stats & Engagement ---
            'fan_count', 'followers_count', 'new_like_count', 
            'talking_about_count', 'were_here_count', 'checkins',
            'rating_count', 'overall_star_rating',
            
            # --- Business Details ---
            'price_range', 'payment_options', 'founded', 'mission', 
            'products', 'general_info', 'company_overview',
            
            # --- Media ---
            'cover', 'picture{url}'
        ]

        # Convert list to comma-separated string
        fields_str = ",".join(fields_list)

        url = f"{self.base_url}/{self.page_id}"
        params = {
            "access_token": self.token,
            "fields": fields_str
        }

        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   ❌ Facebook Error: {e.response.json().get('error', {}).get('message')}")
            return None

    def display_and_save(self, data):
        if not data:
            print("   ⚠️ No data found.")
            return

        # --- 1. Display Formatted Data ---
        print("\n" + "="*50)
        print(f"   📄 {data.get('name', 'Unknown Page').upper()}")
        print("="*50)
        
        # Identity
        print(f"\n   🆔 IDENTITY")
        print(f"      • ID: {data.get('id')}")
        print(f"      • Handle: @{data.get('username', 'N/A')}")
        print(f"      • Category: {data.get('category', 'N/A')}")
        print(f"      • Status: {data.get('verification_status', 'not_verified')}")
        print(f"      • Bio: {data.get('bio', 'N/A')}")

        # Contact
        print(f"\n   📞 CONTACT")
        emails = data.get('emails', [])
        print(f"      • Email: {emails[0] if emails else 'N/A'}")
        print(f"      • Phone: {data.get('phone', 'N/A')}")
        print(f"      • WhatsApp: {data.get('whatsapp_number', 'N/A')}")
        print(f"      • Website: {data.get('website', 'N/A')}")
        print(f"      • Facebook Link: {data.get('link', 'N/A')}")

        # Location
        print(f"\n   📍 LOCATION")
        loc = data.get('location', {})
        if loc:
            addr = loc.get('street', '')
            city = loc.get('city', '')
            country = loc.get('country', '')
            zip_code = loc.get('zip', '')
            print(f"      • Address: {addr}, {city}, {country} {zip_code}")
            print(f"      • Coordinates: {loc.get('latitude')}, {loc.get('longitude')}")
        else:
            print(f"      • No location data.")

        # Stats
        print(f"\n   📊 METRICS")
        print(f"      • Followers: {data.get('followers_count', 0):,}")
        print(f"      • Likes (Fans): {data.get('fan_count', 0):,}")
        print(f"      • Talking About: {data.get('talking_about_count', 0):,}")
        print(f"      • Check-ins/Were Here: {data.get('were_here_count', 0):,}")
        
        if data.get('overall_star_rating'):
            print(f"      • Rating: {data.get('overall_star_rating')} ⭐ ({data.get('rating_count')} votes)")

        # Details
        print(f"\n   📝 DETAILS")
        print(f"      • Founded: {data.get('founded', 'N/A')}")
        print(f"      • Price Range: {data.get('price_range', 'N/A')}")
        print(f"      • Products: {data.get('products', 'N/A')[:50]}...") # Truncated
        print(f"      • Mission: {data.get('mission', 'N/A')[:50]}...") # Truncated

        # --- 2. Save Full Data to JSON ---
        filename = "page_complete_info.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n" + "-"*50)
            print(f"   💾 ALL data saved to: {filename}")
            print("-"*50)
        except Exception as e:
            logger.error(f"Save Error: {e}")

def main():
    manager = PageInfoManager()
    data = manager.get_full_page_details()
    manager.display_and_save(data)

if __name__ == "__main__":
    main()
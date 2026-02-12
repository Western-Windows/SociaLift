#!/usr/bin/env python3

"""
Filename: get_page_info.py
Version: 1.0
Description:
This script is designed to fetch comprehensive information about a Facebook Page.
It includes features to display and save detailed page information.
"""

import requests
import json
import logging
import sys
from datetime import datetime

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

        fields_list = [
            # --- Basic Identity ---
            'id', 'name', 'username', 'about', 'bio', 'description', 
            'category', 'category_list', 'verification_status', 'is_published',
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

    def save_data(self, data):
        if not data:
            print("   ⚠️ No data found.")
            return

        filename = "./Graph API/JSON/page_complete_info.json"
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
    manager.save_data(data)

if __name__ == "__main__":
    main()
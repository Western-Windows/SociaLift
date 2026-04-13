#!/usr/bin/env python3

import os
import requests
import logging
from typing import List, Dict, Optional
from config import Config
# from refresh_user_token import auto_renew_token # Assuming this exists in your project

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class PageTokenManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.user_token = Config.FACEBOOK_ACCESS_TOKEN
        
        if not self.user_token:
            raise ValueError("❌ Missing FACEBOOK_ACCESS_TOKEN in .env file.")

    def get_page_by_id(self, page_id: str) -> Optional[Dict]:
        """Fetches a specific page's credentials using its ID."""
        # We query the Page ID directly instead of 'me/accounts'
        endpoint = f"{self.base_url}/{page_id}"
        params = {
            "access_token": self.user_token,
            "fields": "id,name,access_token,category",
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def _handle_api_error(self, error):
        """Parses Facebook API errors."""
        try:
            error_data = error.response.json().get("error", {})
            message = error_data.get("message", "Unknown API Error")
            code = error_data.get("code")
            logger.error(f"API Error {code}: {message}")
        except Exception:
            logger.error(f"HTTP Request failed: {error}")

    def update_env_file(self, page_id: str, page_token: str):
        """Updates the local .env file."""
        env_path = "Graph API/.env"
        try:
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    lines = f.readlines()

            new_lines = []
            keys_updated = {"FACEBOOK_PAGE_ID": False, "FACEBOOK_PAGE_ACCESS_TOKEN": False}

            for line in lines:
                if line.startswith("FACEBOOK_PAGE_ID="):
                    new_lines.append(f"FACEBOOK_PAGE_ID={page_id}\n")
                    keys_updated["FACEBOOK_PAGE_ID"] = True
                elif line.startswith("FACEBOOK_PAGE_ACCESS_TOKEN="):
                    new_lines.append(f"FACEBOOK_PAGE_ACCESS_TOKEN={page_token}\n")
                    keys_updated["FACEBOOK_PAGE_ACCESS_TOKEN"] = True
                else:
                    new_lines.append(line)

            if not keys_updated["FACEBOOK_PAGE_ID"]:
                new_lines.append(f"FACEBOOK_PAGE_ID={page_id}\n")
            if not keys_updated["FACEBOOK_PAGE_ACCESS_TOKEN"]:
                new_lines.append(f"FACEBOOK_PAGE_ACCESS_TOKEN={page_token}\n")

            with open(env_path, "w") as f:
                f.writelines(new_lines)
            
            print(f"✅ Successfully updated .env with Page ID: {page_id}")
        except Exception as e:
            logger.error(f"Failed to update .env file: {e}")

def main():
    print("🔍 Facebook Page Token Fetcher (by ID)")
    print("=" * 40)
    
    # auto_renew_token() # Enable if you need to refresh user token first

    try:
        manager = PageTokenManager()
        
        # You can prompt for the ID or hardcode it
        target_id = input("Enter the Facebook Page ID (e.g., 803563356170307): ").strip()
        
        if not target_id:
            print("❌ No ID provided.")
            return

        print(f"📡 Fetching credentials for {target_id}...")
        page_data = manager.get_page_by_id(target_id)

        if page_data and "access_token" in page_data:
            print(f"\n✅ Found: {page_data.get('name')}")
            print(f"   Category: {page_data.get('category')}")
            
            confirm = input("\nUpdate .env file with these credentials? (y/n): ").lower()
            if confirm == 'y':
                manager.update_env_file(page_data['id'], page_data['access_token'])
        else:
            print("❌ Could not retrieve token. Ensure your User Access Token has 'pages_read_engagement' and you are an admin of the page.")

    except ValueError as e:
        logger.error(e)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
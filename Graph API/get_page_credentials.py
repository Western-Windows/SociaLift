#!/usr/bin/env python3

"""
Filename: get_page_credentials.py
Version: 1.10
Description:
    This script is designed to manage Facebook Page credentials, including fetching and updating Page Access Tokens.
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from config import Config
from refresh_user_token import auto_renew_token

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class PageTokenManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.user_token = Config.FACEBOOK_ACCESS_TOKEN
        
        if not self.user_token:
            raise ValueError("❌ Missing FACEBOOK_ACCESS_TOKEN in .env file.")

    def get_accounts(self) -> List[Dict]:
        """Fetches all pages associated with the user token."""
        endpoint = f"{self.base_url}/me/accounts"
        params = {
            "access_token": self.user_token,
            "fields": "id,name,access_token,category,tasks",
            "limit": 100
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
            
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e)
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def _handle_api_error(self, error):
        """Parses Facebook API errors for better user feedback."""
        try:
            error_data = error.response.json().get("error", {})
            message = error_data.get("message", "Unknown API Error")
            code = error_data.get("code")
            
            logger.error(f"API Error {code}: {message}")
            
            if code == 190:
                print("💡 Hint: Your User Access Token has expired. Please generate a new one.")
            elif "pages_show_list" in message:
                print("💡 Hint: Your token is missing the 'pages_show_list' permission.")
                
        except Exception:
            logger.error(f"HTTP Request failed: {error}")

    def update_env_file(self, page_id: str, page_token: str):
        """Updates the local .env file with the chosen page credentials."""
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
    print("🔍 Facebook Page Token Manager")
    print("=" * 40)
    auto_renew_token()
    try:
        manager = PageTokenManager()
        pages = manager.get_accounts()

        if not pages:
            print("❌ No pages found. Check your permissions.")
            return

        print(f"✅ Found {len(pages)} pages:\n")
        
        for i, page in enumerate(pages, 1):
            print(f"{i}. {page.get('name')} (Category: {page.get('category')})")
            print(f"   ID: {page.get('id')}")
            print("-" * 40)

        choice = input("\nEnter the number of the page you want to use (or 0 to exit): ")
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(pages):
                selected_page = pages[idx]
                token = selected_page.get("access_token")
                pid = selected_page.get("id")
                print(f"\n✅ Selected: {selected_page.get('name')}")
                manager.update_env_file(pid, token)
            else:
                print("❌ Invalid selection.")
        else:
            print("❌ Invalid input.")

    except ValueError as e:
        logger.error(e)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    main()
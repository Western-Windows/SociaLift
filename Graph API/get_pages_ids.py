import requests
import logging
import json  # Added for JSON support
import os
from config import Config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class UniversalPageFetcher:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.user_token = Config.FACEBOOK_ACCESS_TOKEN
        self.output_file = "./Graph API/JSON/linked_pages.json" # The filename for your JSON
        
        if not self.user_token:
            raise ValueError("❌ Missing FACEBOOK_ACCESS_TOKEN in config.")

    def fetch_all_possible_pages(self):
        """Tries multiple endpoints to find pages linked to the user/app."""
        found_pages = {}

        # Method 1: Standard Accounts
        self._query_endpoint("me/accounts", found_pages)

        # Method 2: Assigned Pages (Crucial for Business Apps / Live Mode)
        self._query_endpoint("me/assigned_pages", found_pages)

        return list(found_pages.values())

    def _query_endpoint(self, path, storage):
        """Helper to query an endpoint and store unique pages."""
        url = f"{self.base_url}/{path}"
        params = {
            "access_token": self.user_token,
            "fields": "id,name,access_token,tasks,category"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json().get("data", [])
            for page in data:
                if page['id'] not in storage:
                    storage[page['id']] = page
        except Exception as e:
            logger.debug(f"Endpoint {path} failed: {e}")

    def save_to_json(self, pages):
        """Saves the list of page data to a JSON file."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(pages, f, indent=4)
            print(f"📂 Successfully saved credentials to: {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")

def main():
    print("🔍 Searching for all linked Facebook Pages...")
    fetcher = UniversalPageFetcher()
    pages = fetcher.fetch_all_possible_pages()

    if not pages:
        print("\n❌ No pages found automatically.")
        print("💡 Tip: Ensure your User Token has 'business_management' and 'pages_show_list'.")
        return

    print(f"\n✅ Found {len(pages)} unique pages:")
    print("=" * 50)
    for i, p in enumerate(pages, 1):
        print(f"{i}. {p['name']} (ID: {p['id']})")
    print("=" * 50)

    # Save the data
    fetcher.save_to_json(pages)

if __name__ == "__main__":
    main()
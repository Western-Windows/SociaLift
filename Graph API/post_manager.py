#!/usr/bin/env python3
"""
Facebook Post Manager
Features:
1. Edit an existing post's message.
2. Delete a post permanently by ID.
"""

import requests
import logging
import sys

# Try to import config
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found. Please ensure you have the configuration file.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class FacebookPostManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        
        if not self.token or not self.page_id:
            print("❌ Credentials missing. Check .env file.")
            sys.exit(1)
        
        self.session = requests.Session()

    def _request(self, method, endpoint, params=None, data=None):
        """Centralized request handler."""
        url = f"{self.base_url}/{endpoint}"
        if not params: params = {}
        params['access_token'] = self.token

        try:
            response = self.session.request(method, url, params=params, json=data)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_msg = e.response.json().get('error', {}).get('message', str(e))
                except:
                    error_msg = e.response.text
            return {'success': False, 'error': error_msg}

    def edit_post(self, post_id, new_message):
        """Updates the text content of a post."""
        print(f"   📝 Updating Post {post_id}...")
        
        # To edit, we send a POST request to the post ID with the new message
        result = self._request(
            method="POST", 
            endpoint=post_id, 
            data={"message": new_message}
        )
        return result

    def delete_post(self, post_id):
        """Permanently deletes a post."""
        print(f"   🗑️  Deleting Post {post_id}...")
        
        # To delete, we send a DELETE request to the post ID
        result = self._request(
            method="DELETE", 
            endpoint=post_id
        )
        return result

# ==========================
# 🎮 Interactive Main
# ==========================

def get_input(prompt):
    return input(f"   🔹 {prompt}: ").strip()

def main():
    manager = FacebookPostManager()

    while True:
        print("\n" + "=" * 40)
        print("   🛠️  FACEBOOK POST MANAGER")
        print("=" * 40)
        print("   1. ✏️  Edit a Post")
        print("   2. 🗑️  Delete a Post")
        print("   0. 🚪 Exit")
        print("-" * 40)

        choice = get_input("Select option")

        if choice == "0":
            print("   👋 Goodbye!")
            sys.exit(0)

        # --- EDIT POST ---
        elif choice == "1":
            pid = get_input("Enter Post ID to Edit")
            if not pid: continue
            
            new_text = get_input("Enter New Message")
            if not new_text: 
                print("   ⚠️ Message cannot be empty.")
                continue

            result = manager.edit_post(pid, new_text)
            if result['success']:
                print("   ✅ Success! Post updated.")
            else:
                print(f"   ❌ Failed: {result['error']}")

        # --- DELETE POST ---
        elif choice == "2":
            pid = get_input("Enter Post ID to DELETE")
            if not pid: continue

            result = manager.delete_post(pid)
            if result['success']:
                print("   ✅ Success! Post deleted.")
            else:
                print(f"   ❌ Failed: {result['error']}")
        else:
            print("   ❌ Invalid option.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
Filename: comment_reply.py
Version: 1.10
Description:
This script is designed to reply to Facebook comments by its ID and like them.
"""

import requests
import logging
import sys
from typing import Dict

try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FacebookBot:
    """Handles direct interactions with Facebook Comments."""

    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.access_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.session = requests.Session()

        if not self.access_token:
            raise ValueError("Missing Access Token")

    def send_reply(self, comment_id, message):
        """Posts a reply to the specific comment ID."""
        url = f"{self.base_url}/{comment_id}/comments"
        params = {'access_token': self.access_token}
        data = {'message': message}
        
        try:
            response = self.session.post(url, params=params, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Reply failed: {e}")
            return False

    def like_comment(self, comment_id: str) -> Dict:
        """
        Likes a specific comment using the dedicated /likes endpoint.
        """
        params = {
            'access_token': self.access_token
        }

        try:
            response = requests.post(f"{self.base_url}/{comment_id}/likes", params=params)
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                return {
                    'success': True,
                    'message': 'Comment liked successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to like comment'
                }
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                error_msg = e.response.json().get('error', {}).get('message', str(e))
                return {'success': False, 'error': error_msg}
            return {
                'success': False,
                'error': f'Failed to like comment: {e}'
            }
        
def get_input(prompt):
    return input(f"   🔹 {prompt}: ").strip()

def print_header():
    print("\n" + "=" * 45)
    print("   🎯 DIRECT COMMENT MANAGER")
    print("=" * 45)


def main():
    try:
        bot = FacebookBot()
    except ValueError:
        print("❌ Config Error: Check your tokens.")
        sys.exit(1)

    print_header()

    comment_id = get_input("Enter Target Comment ID")
    if not comment_id:
        print("   👋 Exiting.")
        sys.exit(0)

    while True:
        print(f"\n   Targeting: {comment_id}")
        print("   1. ↩️  Reply (Text)")
        print("   2. 👍 Like Comment") 
        print("   3. 🆕 Change Target ID")
        print("   0. 🚪 Exit")
        
        choice = get_input("Choose Action")

        if choice == "0":
            print("   👋 Goodbye!")
            sys.exit(0)

        elif choice == "3":
            comment_id = get_input("Enter New Comment ID")
            if not comment_id: break
            continue

        elif choice == "1":
            msg = get_input("Type your reply")
            if msg:
                print("      ⏳ Sending reply...")
                if bot.send_reply(comment_id, msg):
                    print("      ✅ Success! Reply posted.")
                else:
                    print("      ❌ Failed to reply.")

        elif choice == "2":
            print(f"      ⏳ Liking comment...")
            result = bot.like_comment(comment_id)
            
            if result['success']:
                print(f"      ✅ {result['message']}")
            else:
                print(f"      ❌ {result['error']}")
        
        else:
            print("   ❌ Invalid option.")

        input("\n   Press Enter to continue...")

if __name__ == "__main__":
    main()
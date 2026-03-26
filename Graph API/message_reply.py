#!/usr/bin/env python3

"""
Filename: message_reply.py
Version: 1.0
Description:
This script is designed to send replies to specific user PSIDs on Facebook Messenger.
"""

import requests
import logging
import sys
from typing import Dict, Optional
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class FacebookMessenger:
    """Handles Messenger API interactions."""

    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.access_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.session = requests.Session()

        if not self.access_token:
            raise ValueError("Missing Access Token in .env")

    def send_message(self, recipient_psid: str, message_text: str) -> bool:
        """
        Sends a text message to a specific user (PSID).
        
        Args:
            recipient_psid (str): The Page Scoped ID of the user.
            message_text (str): The text content to send.
            
        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not message_text.strip():
            print("   ⚠️  Cannot send empty message.")
            return False

        url = f"{self.base_url}/me/messages"
        params = {"access_token": self.access_token}
     
        payload = {
            "recipient": {"id": recipient_psid},
            "message": {"text": message_text},
            "messaging_type": "RESPONSE"
        }

        try:
     
            self._send_action(recipient_psid, "typing_on")
           
            response = self.session.post(url, params=params, json=payload)
            response.raise_for_status()

            self._send_action(recipient_psid, "typing_off")
            
            data = response.json()
            msg_id = data.get('message_id', 'Unknown ID')
            print(f"   ✅ Message sent! (ID: {msg_id})")
            return True

        except requests.exceptions.RequestException as e:
            self._handle_error(e)
            return False

    def _send_action(self, psid: str, action: str):
        """Helper to send sender actions like typing_on/off."""
        url = f"{self.base_url}/me/messages"
        payload = {
            "recipient": {"id": psid},
            "sender_action": action
        }
        try:
            self.session.post(url, params={"access_token": self.access_token}, json=payload)
        except:
            pass 

    def _handle_error(self, e):
        """Parses and prints API errors clearly."""
        if hasattr(e, 'response') and e.response is not None:
            try:
                err = e.response.json()
                msg = err.get('error', {}).get('message', str(e))
                code = err.get('error', {}).get('code')
                print(f"   ❌ API Error ({code}): {msg}")
        
                if code == 230:
                    print("      ℹ️  Permissions missing. Check 'pages_messaging'.")
                elif code == 100:
                    print("      ℹ️  Invalid PSID or User has blocked the page.")
            except:
                print(f"   ❌ HTTP Error: {e}")
        else:
            print(f"   ❌ Network Error: {e}")

def get_input(prompt):
    return input(f"   🔹 {prompt}: ").strip()

def main():
    print("\n" + "=" * 45)
    print("   💬 MESSENGER REPLY TOOL")
    print("=" * 45)

    try:
        bot = FacebookMessenger()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    psid = get_input("Enter User PSID (Page Scoped ID)")
    
    if not psid:
        print("   👋 Exiting.")
        sys.exit(0)

    print(f"\n   Targeting User: {psid}")
    print("   (Type 'exit' to quit)\n")

    while True:
        msg = get_input("Type message")
        
        if msg.lower() in ['exit', 'quit', 'q']:
            print("   👋 Goodbye!")
            break

        print("      ⏳ Sending...")
        bot.send_message(psid, msg)
        print("-" * 30)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
Filename: get_messages.py
Version: 1.10
Description:
This script is designed to fetch messages from Facebook Messenger.
It includes features to fetch full conversation history, unread messages.
"""

import os
import json
import logging
import sys
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional

try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found. Please ensure you have the configuration file.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class MessengerDataManager:
    def __init__(self):
        self.page_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.base_url = "https://graph.facebook.com/v24.0"
        
        if not self.page_token or not self.page_id:
            print("❌ Missing Credentials. Check .env file.")
            sys.exit(1)
            
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Centralized request handler."""
        url = f"{self.base_url}/{endpoint}"
        if params is None: params = {}
        params['access_token'] = self.page_token
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"API Error ({endpoint}): {e}")
            return None
        except Exception as e:
            logger.error(f"Network Error: {e}")
            return None

    def get_conversations(self, limit: int = 20) -> List[Dict]:
        """Fetches conversations including unread status."""
        fields = "id,updated_time,message_count,unread_count,snippet,participants"
        endpoint = f"{self.page_id}/conversations"
        params = {"limit": limit, "fields": fields}
        
        data = self._make_request(endpoint, params)
        return data.get('data', []) if data else []

    def get_messages(self, conversation_id: str, limit: int = 20) -> List[Dict]:
        """Fetches message history for a specific conversation."""
        fields = "id,created_time,message,from,attachments"
        endpoint = f"{conversation_id}/messages"
        params = {"limit": limit, "fields": fields}
        
        data = self._make_request(endpoint, params)
        return data.get('data', []) if data else []

    def unread_messages(self, conv_limit: int, msg_limit: int, unread_only: bool = False) -> List[Dict]:
        """
        Main logic to fetch and merge data.
        If unread_only=True, skips conversations with 0 unread messages.
        """
        print(f"📥 Fetching last {conv_limit} conversations...")
        raw_conversations = self.get_conversations(conv_limit)
        
        final_data = []
        processed_count = 0

        if not raw_conversations:
            print("   ⚠️ No conversations found.")
            return []

        print(f"🔄 Processing data (Unread Only: {unread_only})...")

        for conv in raw_conversations:
            unread_count = conv.get('unread_count', 0)
            if unread_only and unread_count == 0:
                continue

            conv_id = conv.get('id')
            updated = conv.get('updated_time')
            participants_raw = conv.get('participants', {}).get('data', [])
            clean_participants = []
            for p in participants_raw:
                if p.get('id') != self.page_id:
                    clean_participants.append({
                        "psid": p.get('id'),
                        "name": p.get('name', 'Unknown')
                    })

            messages_raw = self.get_messages(conv_id, msg_limit)
            clean_messages = []
            for m in messages_raw:
                sender = m.get('from', {})
                clean_messages.append({
                    "message_id": m.get('id'),
                    "timestamp": m.get('created_time'),
                    "sender_name": sender.get('name'),
                    "content": m.get('message'),
                    "has_attachment": 'attachments' in m
                })

            final_data.append({
                "conversation_id": conv_id,
                "status": "unread" if unread_count > 0 else "read",
                "unread_count": unread_count,
                "last_updated": updated,
                "participants": clean_participants,
                "messages": clean_messages
            })
            
            processed_count += 1

        return final_data

    def export_to_json(self, data, filename):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Saved {len(data)} conversations to '{filename}'")
        except Exception as e:
            print(f"❌ Failed to write JSON: {e}")

def get_int_input(prompt: str, default: int) -> int:
    val = input(f"   🔹 {prompt} (default {default}): ").strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        print(f"      ❌ Invalid number. Using default {default}.")
        return default

def print_header():
    print("\n" + "=" * 40)
    print("   🚀 MESSENGER DATA EXTRACTOR")
    print("=" * 40)

def main():
    manager = MessengerDataManager()

    while True:
        print_header()
        print("   1. 📂 Download Full History")
        print("   2. 🔔 Download Unread Messages Only")
        print("   0. 🚪 Exit")
        print("-" * 40)

        choice = input("   👉 Select option: ").strip()

        if choice == "0":
            print("   👋 Goodbye!")
            sys.exit(0)

        elif choice in ["1", "2"]:

            unread_mode = (choice == "2")
            mode_name = "Unread" if unread_mode else "Full"
            default_filename = "./Graph API/JSON/messenger_unread.json" if unread_mode else "./Graph API/JSON/messenger_full.json"

            print(f"\n   [Settings for {mode_name} Export]")
            conv_limit = get_int_input("Conversations to check", 20)
            msg_limit = get_int_input("Messages per chat", 20)
            filename = default_filename

            print("\n   ⏳ Starting extraction...")
            data = manager.unread_messages(conv_limit, msg_limit, unread_only=unread_mode)

            if data:
                manager.export_to_json(data, filename)
            else:
                if unread_mode:
                    print("\n   ✅ No unread conversations found!")
                else:
                    print("\n   ⚠️ No data found.")
        
        else:
            print("   ❌ Invalid selection.")
            time.sleep(1)

if __name__ == "__main__":
    main()
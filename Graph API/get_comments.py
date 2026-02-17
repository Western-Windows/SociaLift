#!/usr/bin/env python3
"""
Facebook Comment Fetcher (Detailed)
Features:
1. Fetches Top-Level Comments AND Replies.
2. Identifies 'is_reply' status and links to 'reply_to_id'.
3. Custom filename for specific post scans.
"""

import requests
import json
import logging
import sys
import time
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class FacebookFetcher:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        
        if not self.token or not self.page_id:
            print("❌ Credentials missing. Check .env file.")
            sys.exit(1)

    def get_page_posts(self, limit=5):
        """Fetches the most recent posts from the page."""
        url = f"{self.base_url}/{self.page_id}/posts"
        params = {
            "access_token": self.token,
            "fields": "id,message,created_time",
            "limit": limit
        }
        
        print(f"   📥 Fetching last {limit} posts from page...")
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to fetch posts: {e}")
            return []

    def get_comments(self, post_id):
        """
        Fetches Top-Level comments AND their Replies.
        """
        all_items = []
        
        fields = (
            "id,message,created_time,like_count,permalink_url,from{id},"
            "comments.limit(500){id,message,created_time,like_count,permalink_url,from{id}}"
        )
        
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "access_token": self.token,
            "fields": fields,
            "limit": 50
        }

        print(f"   🔍 Fetching comments for Post {post_id}...")
        
        while url:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data:
                    all_items.extend(data['data'])
                
                if 'paging' in data and 'next' in data['paging']:
                    url = data['paging']['next']
                    params = {}
                else:
                    url = None

            except Exception as e:
                logger.error(f"Error fetching comments: {e}")
                break

        return all_items

    def save_to_json(self, data, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   💾 Saved data to '{filename}'")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")

# ==========================
# 🎮 Interactive Main
# ==========================

def get_int_input(prompt, default=None):
    while True:
        try:
            val = input(f"   🔹 {prompt}: ").strip()
            if not val and default is not None:
                return default
            return int(val)
        except ValueError:
            print("      ❌ Please enter a valid number.")

def main():
    fetcher = FacebookFetcher()

    while True:
        print("\n" + "=" * 40)
        print("   💬 FACEBOOK COMMENT MANAGER (DETAILED)")
        print("=" * 40)
        print("   1. 📰 Scan Recent Page Feed")
        print("   2. 📌 Check Specific Post ID")
        print("   0. 🚪 Exit")
        print("-" * 40)

        choice = input("   👉 Select option: ").strip()

        if choice == "0":
            print("   👋 Goodbye!")
            sys.exit(0)

        posts_to_check = []
        is_single_post_mode = False # Flag for filename logic
        
        if choice == "1":
            limit = get_int_input("How many recent posts to scan? (default 5)", 5)
            posts_to_check = fetcher.get_page_posts(limit)
        elif choice == "2":
            pid = input("   🔹 Enter Post ID: ").strip()
            if pid:
                posts_to_check = [{"id": pid, "message": "Specific Post"}]
                is_single_post_mode = True
        else:
            print("   ❌ Invalid choice.")
            continue
        
        # --- Filter Selection ---
        print("\n   [Filter Options]")
        print("   1. Fetch ALL Comments (Including Page Replies)")
        print("   2. Fetch ONLY Unreplied Threads (No Page Reply)")
        
        filter_choice = input("   👉 Select filter (1 or 2): ").strip()
        
        grouped_results = []
        print(f"\n   🚀 Starting Scan...")

        for post in posts_to_check:
            pid = post['id']
            p_message = post.get('message', '')
            
            raw_top_level = fetcher.get_comments(pid)
            
            if not raw_top_level:
                continue

            processed_thread = []

            for top_c in raw_top_level:
                replies_data = top_c.get('comments', {}).get('data', [])
                
                # Check if Page replied in this thread
                page_replied_in_thread = False
                thread_items = []

                # --- 1. Process Top Level Comment ---
                top_id = top_c.get('id')
                top_author_id = top_c.get('from', {}).get('id')
                is_page_top = (top_author_id == fetcher.page_id)
                if is_page_top: page_replied_in_thread = True
                
                thread_items.append({
                    "id": top_id,
                    "message": top_c.get('message'),
                    "created_time": top_c.get('created_time'),
                    "is_by_page": is_page_top,
                    "link": top_c.get('permalink_url'),
                    
                    # ✅ NEW FIELDS: Top level is never a reply
                    "is_reply": False,
                    "reply_to_id": None
                })

                # --- 2. Process Replies ---
                for reply in replies_data:
                    rep_author_id = reply.get('from', {}).get('id')
                    is_page_reply = (rep_author_id == fetcher.page_id)
                    if is_page_reply: page_replied_in_thread = True
                    
                    thread_items.append({
                        "id": reply.get('id'),
                        "message": reply.get('message'),
                        "created_time": reply.get('created_time'),
                        "is_by_page": is_page_reply,
                        "link": reply.get('permalink_url'),
                        
                        # ✅ NEW FIELDS: Identify reply & link to parent
                        "is_reply": True,
                        "reply_to_id": top_id
                    })

                # --- Apply Logic ---
                if filter_choice == "2":
                    # Unreplied Logic
                    if page_replied_in_thread: continue
                    if is_page_top: continue
                    processed_thread.extend(thread_items)
                else:
                    # All Comments Logic
                    processed_thread.extend(thread_items)

            # Add to results
            if processed_thread:
                count = len(processed_thread)
                print(f"      👉 Post {pid}: Found {count} items.")
                
                grouped_results.append({
                    "post_id": pid,
                    "post_snippet": p_message[:50],
                    "total_matches": count,
                    "comments": processed_thread
                })

        # --- Save with Custom Filename ---
        if grouped_results:
            if is_single_post_mode and len(posts_to_check) == 1:
                # ✅ Custom Name for Specific Post
                specific_id = posts_to_check[0]['id']
                filename = f"post_{specific_id}_comments.json"
            else:
                # Generic Name for Feed Scan
                suffix = "all" if filter_choice == "1" else "unreplied_threads"
                filename = f"comments_{suffix}.json"
                
            fetcher.save_to_json(grouped_results, filename)
        else:
            print("\n   ✅ No matching comments found.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3

"""
Filename: get_comments.py
Version: 2.0
Description:
This script fetches comments from Facebook posts using the Graph API, with options to filter for unreplied threads.
It retrieves both top-level comments and their replies, checks if the page has replied, and saves the results in a structured JSON format.
"""

import os
from pathlib import Path
import requests
import json
import logging
import sys

_JSON_DIR = Path(__file__).parent / "JSON"
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

    def get_raw_comments(self, post_id):
        """
        Fetches Top-Level comments AND their Replies from API.
        Returns a raw list of comment objects.
        """
        all_items = []
        fields = (
            "id,message,created_time,like_count,permalink_url,from{id},"
            "comments.limit(500){id,message,created_time,like_count,permalink_url,from{id}}"
        )
        url = f"{self.base_url}/{post_id}/comments"
        params = {"access_token": self.token, "fields": fields, "limit": 50}

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
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   💾 Saved data to '{filename}'")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")

def process_single_post(fetcher, post, filter_mode):
    """
    Fetches and filters comments for a single post.
    Returns a dict with post details and filtered comments, or None if empty.
    filter_mode: "1" (All), "2" (Unreplied only)
    """
    pid = post['id']
    raw_comments = fetcher.get_raw_comments(pid)
    
    if not raw_comments:
        return None

    valid_threads = []

    for top_c in raw_comments:
        thread_data = parse_thread(top_c, fetcher.page_id)

        if filter_mode == "2":

            if thread_data['page_replied'] or thread_data['is_page_top']:
                continue

        valid_threads.extend(thread_data['items'])

    if not valid_threads:
        return None

    return {
        "post_id": pid,
        "post_snippet": post.get('message', '')[:50],
        "total_matches": len(valid_threads),
        "comments": valid_threads
    }

def parse_thread(top_comment, page_id):
    """
    Parses a top-level comment and its replies.
    Returns metadata about the thread (e.g., did the page reply?).
    """
    items = []
    page_replied = False
    
    top_author_id = top_comment.get('from', {}).get('id')
    is_page_top = (top_author_id == page_id)
    if is_page_top: page_replied = True

    items.append({
        "id": top_comment.get('id'),
        "message": top_comment.get('message'),
        "created_time": top_comment.get('created_time'),
        "is_by_page": is_page_top,
        "link": top_comment.get('permalink_url'),
        "is_reply": False
    })

    replies = top_comment.get('comments', {}).get('data', [])
    for reply in replies:
        rep_author_id = reply.get('from', {}).get('id')
        is_page_reply = (rep_author_id == page_id)
        if is_page_reply: page_replied = True

        items.append({
            "id": reply.get('id'),
            "message": reply.get('message'),
            "created_time": reply.get('created_time'),
            "is_by_page": is_page_reply,
            "link": reply.get('permalink_url'),
            "is_reply": True,
            "reply_to_id": top_comment.get('id')
        })

    return {
        "items": items,
        "page_replied": page_replied,
        "is_page_top": is_page_top
    }

def get_int_input(prompt, default=None):
    while True:
        try:
            val = input(f"   🔹 {prompt}: ").strip()
            if not val and default is not None:
                return default
            return int(val)
        except ValueError:
            print("      ❌ Please enter a valid number.")

def get_target_posts(fetcher):
    """Asks user what to scan (Feed vs Specific ID). Returns list of post dicts."""
    print("\n" + "=" * 40)
    print("   💬 FACEBOOK COMMENT MANAGER")
    print("=" * 40)
    print("   1. 📰 Scan Recent Page Feed")
    print("   2. 📌 Check Specific Post ID")
    print("   0. 🚪 Exit")
    print("-" * 40)

    choice = input("   👉 Select option: ").strip()

    if choice == "0":
        print("   👋 Goodbye!")
        sys.exit(0)

    if choice == "1":
        limit = get_int_input("How many recent posts? (default 5)", 5)
        return fetcher.get_page_posts(limit)
    
    elif choice == "2":
        pid = input("   🔹 Enter Post ID: ").strip()
        if pid:
            return [{"id": pid, "message": "Specific Post Request"}]
    
    print("   ❌ Invalid choice.")
    return []

def run_interactive_mode():
    fetcher = FacebookFetcher()

    while True:
        posts = get_target_posts(fetcher)
        if not posts: continue

        print("\n   [Filter Options]")
        print("   1. Fetch ALL Comments")
        print("   2. Fetch ONLY Unreplied Threads")
        filter_choice = input("   👉 Select filter (1 or 2): ").strip()
        
        results = []
        print(f"\n   🚀 Starting Scan...")
        
        for post in posts:
            data = process_single_post(fetcher, post, filter_choice)
            if data:
                print(f"      👉 Post {post['id']}: Found {data['total_matches']} items.")
                results.append(data)

        if results:
            if len(posts) == 1:
                filename = str(_JSON_DIR / f"post_{posts[0]['id']}_comments.json")
            else:
                suffix = "all" if filter_choice == "1" else "unreplied"
                filename = str(_JSON_DIR / f"comments_{suffix}.json")
            
            fetcher.save_to_json(results, filename)
        else:
            print("\n   ✅ No matching comments found.")

if __name__ == "__main__":
    run_interactive_mode()
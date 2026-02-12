#!/usr/bin/env python3
import requests
import json
import logging
import time
import sys
from datetime import datetime
from typing import List, Dict, Optional

"""
Filename: get_posts_insights.py
Version: 1.0
Description:
This script fetches and processes insights data for Facebook posts.
"""

try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found. Please ensure you have the configuration file.")
    sys.exit(1)

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class FacebookAnalyticsManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.session = requests.Session()
        
        if not self.token or not self.page_id:
            print("❌ Credentials missing in .env file.")
            sys.exit(1)

    def _api_call(self, endpoint, params=None):
        """Robust API handler."""
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint}"
        params = params or {}
        params['access_token'] = self.token
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"⚠️ Request failed: {e}")
            return None


    def _get_fields_string(self):
        """
        Returns the API fields string.
        We added the requested metrics to the insights.metric() call here.
        """
        return (
            "id,message,created_time,permalink_url,"
            "shares,"
            "reactions.summary(true).limit(0),"
            "comments.summary(true).limit(0),"
            "insights.metric("
                "post_reactions_by_type_total,"
                "post_media_view,"
                "post_impressions_unique,"
                "post_clicks"
            ").period(lifetime)"
        )

    def get_posts(self, limit: Optional[int] = None) -> List[Dict]:
        """Fetches posts (All or Top K)."""
        mode_str = f"top {limit}" if limit else "ALL"
        print(f"📥 Fetching {mode_str} posts with insights...")
        
        all_posts = []
        fields = self._get_fields_string()
        
        api_limit = min(limit, 25) if limit else 25
        
        url = f"{self.base_url}/{self.page_id}/posts"
        params = {"fields": fields, "limit": api_limit}

        while url:
            data = self._api_call(url, params)
            if not data or 'data' not in data:
                break

            current_batch = data['data']
            all_posts.extend(current_batch)
            print(f"   ...fetched {len(current_batch)} posts (Total: {len(all_posts)})")

            if limit and len(all_posts) >= limit:
                all_posts = all_posts[:limit]
                break

            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
                params = {}
                time.sleep(0.5)
            else:
                url = None

        return all_posts

    def get_single_post(self, post_id: str) -> List[Dict]:
        """Fetches a single post."""
        print(f"📥 Fetching details for Post ID: {post_id}...")
        fields = self._get_fields_string()
        
        data = self._api_call(post_id, {"fields": fields})
        
        if data and 'id' in data:
            print("   ✅ Post found.")
            return [data]
        else:
            print("   ❌ Post not found or permission denied.")
            return []

    def get_all_comments_for_post(self, post_id):
        """Fetches ALL comments for a specific post."""
        all_comments = []
        fields = "id,message,created_time,like_count,from{id,name,picture}"
        url = f"{self.base_url}/{post_id}/comments"
        params = {"fields": fields, "limit": 50}

        while url:
            data = self._api_call(url, params)
            if not data or 'data' not in data:
                break
            
            for c in data['data']:
                clean_comment = {
                    "id": c.get('id'),
                    "message": c.get('message'),
                    "created_time": c.get('created_time'),
                    "likes": c.get('like_count', 0)
  
                }
                all_comments.append(clean_comment)

            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
                params = {}
            else:
                url = None
        
        return all_comments


    def process_data(self, raw_posts: List[Dict]):
        """Cleans data and extracts the specific insights requested."""
        if not raw_posts:
            return []

        final_dataset = []
        print(f"\n🔄 Processing {len(raw_posts)} posts to get comments & insights...")
        
        for index, post in enumerate(raw_posts, 1):
            print(f"   Processing {index}/{len(raw_posts)}: {post.get('id')}...")

            stats = {
                "shares": post.get('shares', {}).get('count', 0),
                "likes": post.get('reactions', {}).get('summary', {}).get('total_count', 0),
                "comments_count": post.get('comments', {}).get('summary', {}).get('total_count', 0),
            }

            insights_data = {
                "views": 0,     
                "reach": 0,      
                "total_clicks": 0,    
                "reactions_breakdown": {} 
            }

            if 'insights' in post and 'data' in post['insights']:
                for item in post['insights']['data']:
                    name = item.get('name')
                    try:
                        val = item['values'][0]['value']
                        
                        if name == 'post_media_view':
                            insights_data['views'] = val
                        elif name == 'post_impressions_unique':
                            insights_data['reach'] = val
                        elif name == 'post_clicks':
                            insights_data['total_clicks'] = val
                        elif name == 'post_reactions_by_type_total':
                            insights_data['reactions_breakdown'] = val
                            
                    except (KeyError, IndexError):
                        pass

            clean_post = {
                "post_id": post.get('id'),
                "published_date": post.get('created_time'),
                "message": post.get('message', ''),
                "url": post.get('permalink_url'),
                "engagement_stats": stats,
                "performance_metrics": insights_data,
            }
            final_dataset.append(clean_post)

        return final_dataset

    def export_to_json(self, data, filename="fb_analytics.json"):
        """Exports data to JSON."""
        output = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "page_id": self.page_id,
                "total_posts": len(data)
            },
            "data": data
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"\n🎉 Success! Exported to {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to write JSON: {e}")

def get_int_input(prompt):
    while True:
        try:
            val = input(f"   🔹 {prompt}: ").strip()
            return int(val)
        except ValueError:
            print("      ❌ Please enter a valid number.")

def main():
    manager = FacebookAnalyticsManager()

    while True:
        print("\n" + "=" * 40)
        print("   📊 FACEBOOK ANALYTICS TOOL")
        print("=" * 40)
        print("   1. 🌍 Fetch ALL Posts (Full History)")
        print("   2. ⚡ Fetch Top K Recent Posts")
        print("   3. 🔎 Fetch Single Post (by ID)")
        print("   0. 🚪 Exit")
        print("-" * 40)

        choice = input("   👉 Select option: ").strip()

        raw_posts = []
        filename = "./Graph API/JSON/fb_data.json"

        if choice == "0":
            print("   👋 Goodbye!")
            sys.exit(0)

        elif choice == "1":
            raw_posts = manager.get_posts(limit=None)
            filename = "./Graph API/JSON/fb_full_history.json"

        elif choice == "2":
            k = get_int_input("Enter number of posts (K)")
            raw_posts = manager.get_posts(limit=k)
            filename = f"./Graph API/JSON/fb_recent_{k}.json"

        elif choice == "3":
            pid = input("   🔹 Enter Post ID: ").strip()
            if pid:
                raw_posts = manager.get_single_post(pid)
                filename = f"./Graph API/JSON/fb_post_{pid}.json"

        else:
            print("   ❌ Invalid selection.")
            continue

        if raw_posts:
            clean_data = manager.process_data(raw_posts)
            manager.export_to_json(clean_data, filename)
        

if __name__ == "__main__":
    main()
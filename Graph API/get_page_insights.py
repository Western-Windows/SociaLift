import os
import requests
import json
import logging
import sys
import pandas as pd
from datetime import datetime, timedelta

"""
Filename: get_page_insights.py
Version: 1.0
Description:
This script fetches and processes insights data for a Facebook Page.
"""

try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class PageInsightsFetcher:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.access_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        
        # 1. Metric Mapping
        self.metric_map = {
            "page_post_engagements": "page_post_engagements",
            "page_daily_follows": "page_daily_follows",
            "page_daily_follows_unique": "page_daily_follows_unique",
            "page_daily_unfollows_unique": "page_daily_unfollows_unique",
            "page_follows": "page_follows",
            "page_impressions_unique": "page_impressions_unique",
            "page_impressions_viral_unique": "page_impressions_viral_unique",
            "page_impressions_nonviral_unique": "page_impressions_nonviral_unique",
            "page_media_view": "page_video_views",
            "page_actions_post_reactions_like_total": "page_actions_post_reactions_like_total",
            "page_actions_post_reactions_love_total": "page_actions_post_reactions_love_total",
            "page_actions_post_reactions_wow_total": "page_actions_post_reactions_wow_total",
            "page_actions_post_reactions_haha_total": "page_actions_post_reactions_haha_total",
            "page_actions_post_reactions_sorry_total": "page_actions_post_reactions_sorry_total",
            "page_actions_post_reactions_anger_total": "page_actions_post_reactions_anger_total",
            "page_actions_post_reactions_total": "page_actions_post_reactions_total"
        }
        self.aggregation_rules = {
            "page_follows": "last"
        }

        # 2. Explanations
        self.explanations = {
            "page_post_engagements": "Total number of times people engaged with your posts (likes, comments, shares, clicks).",
            "page_daily_follows": "The number of new people who liked/followed your Page (Monthly Sum).",
            "page_daily_follows_unique": "The number of unique new people who liked/followed your Page (Monthly Sum).",
            "page_daily_unfollows_unique": "The number of people who unliked/unfollowed your Page (Monthly Sum).",
            "page_follows": "The total number of people who like/follow your Page (Month-End Snapshot).",
            "page_impressions_unique": "The number of people who saw any content from your Page (Reach).",
            "page_impressions_viral_unique": "The number of people who saw your page content because a friend engaged with it.",
            "page_impressions_nonviral_unique": "The number of people who saw your page content directly, not through a friend's action.",
            "page_media_view": "Total number of times videos/media on your page were viewed for at least 3 seconds.",
            "page_actions_post_reactions_like_total": "Total number of 'Like' reactions on your Page's posts.",
            "page_actions_post_reactions_love_total": "Total number of 'Love' reactions on your Page's posts.",
            "page_actions_post_reactions_wow_total": "Total number of 'Wow' reactions on your Page's posts.",
            "page_actions_post_reactions_haha_total": "Total number of 'Haha' reactions on your Page's posts.",
            "page_actions_post_reactions_sorry_total": "Total number of 'Sad/Sorry' reactions on your Page's posts.",
            "page_actions_post_reactions_anger_total": "Total number of 'Angry' reactions on your Page's posts.",
            "page_actions_post_reactions_total": "Total number of all reactions (Like, Love, Wow, etc.) on your Page's posts."
        }

    def fetch_insights(self, days_ago=90):
        """
        Fetches insights for the last 'days_ago' days.
        """
        daily_raw_data = []
        until = datetime.now()
        since = until - timedelta(days=days_ago)
        
        print(f"⏳ Fetching daily insights from {since.date()} to {until.date()}...")

        for user_name, api_metric in self.metric_map.items():
            period = "lifetime" if api_metric == "page_fans" else "day"

            url = f"{self.base_url}/{self.page_id}/insights"
            params = {
                "access_token": self.access_token,
                "metric": api_metric,
                "period": period,
                "since": int(since.timestamp()),
                "until": int(until.timestamp())
            }

            try:
                response = requests.get(url, params=params)
                data = response.json()

                if "error" in data:
                    logger.warning(f"⚠️ API Warning for {user_name}: {data['error']['message']}")
                    continue
                
                if "data" in data and len(data["data"]) > 0:
                    metric_data = data["data"][0]
                    values = metric_data.get("values", [])

                    for entry in values:
                        raw_val = entry.get("value", 0)
            
                        if isinstance(raw_val, dict):
                     
                            cleaned_val = sum(raw_val.values())
                        else:
                            cleaned_val = raw_val

                        daily_raw_data.append({
                            "metric": user_name,
                            "date": entry.get("end_time", "")[:10],
                            "value": cleaned_val 
                        })

            except Exception as e:
                logger.error(f"Request failed for {user_name}: {e}")

        return daily_raw_data

    def group_and_aggregate(self, daily_data):
        if not daily_data: return []

        print("\n🔄 Aggregating by Month (Summing daily counts, taking Snapshot for followers)...")
        
        df = pd.DataFrame(daily_data)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value']).fillna(0)

        month_map = {}

        for metric in df['metric'].unique():
            metric_df = df[df['metric'] == metric].copy()
            metric_df.set_index('date', inplace=True)
       
            rule = self.aggregation_rules.get(metric, 'sum')
          
            try:
                resampled = metric_df.resample('ME')['value'].agg(rule)
            except ValueError:
                resampled = metric_df.resample('M')['value'].agg(rule)
            
            for date_idx, val in resampled.items():

                if pd.notna(val):
                    month_key = date_idx.strftime('%Y-%m')
                    
                    if month_key not in month_map:
                        month_map[month_key] = {"month": month_key}
   
                    month_map[month_key][metric] = {
                        "value": int(val),
                        "explanation": self.explanations.get(metric, "")
                    }

        final_list = sorted(list(month_map.values()), key=lambda x: x['month'])
        return final_list

    def save_to_json(self, data, filename="./Graph API/JSON/monthly_detailed_insights.json"):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"\n💾 Monthly data saved to: {filename}")
            print(f"📊 Total Months Processed: {len(data)}")
        except Exception as e:
            logger.error(f"Save failed: {e}")

if __name__ == "__main__":
    fetcher = PageInsightsFetcher()

    daily_raw = fetcher.fetch_insights(days_ago=60)
    
    if daily_raw:
        grouped_data = fetcher.group_and_aggregate(daily_raw)

        fetcher.save_to_json(grouped_data)
    else:
        print("⚠️ No data found.")
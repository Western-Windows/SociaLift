## UNFINISHED - DO NOT USE THIS FILE YET ##

import requests
import json
import sys
from datetime import datetime
from dateutil import parser  # Requires: pip install python-dateutil

# --- 1. CONFIGURATION FIX ---
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

PAGE_ID = Config.FACEBOOK_PAGE_ID
ACCESS_TOKEN = Config.FACEBOOK_PAGE_ACCESS_TOKEN
BASE_URL = "https://graph.facebook.com/v19.0"
# ----------------------------

def fetch_insights(metric, period):
    """
    Fetches Page Insights (Works for Day/Week/Month)
    """
    url = f"{BASE_URL}/{PAGE_ID}/insights"
    params = {
        "metric": metric,
        "period": period,
        "access_token": ACCESS_TOKEN
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        raise Exception(f"Insights API Error: {r.text}")

    return r.json().get("data", [{}])[0].get("values", [])

def fetch_hourly_activity():
    """
    WORKAROUND: Since 'page_views' doesn't support 'hour', 
    we calculate hourly traffic by analyzing recent Post Impressions.
    """
    url = f"{BASE_URL}/{PAGE_ID}/posts"
    params = {
        "access_token": ACCESS_TOKEN,
        "limit": 50,  # Analyze last 50 posts
        "fields": "created_time,insights.metric(post_impressions_unique)"
    }
    
    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"⚠️ Could not fetch posts for hourly data: {r.text}")
        return []

    # Bucket traffic by Hour (00:00 to 23:00)
    hourly_counts = {h: 0 for h in range(24)}
    
    data = r.json().get("data", [])
    for post in data:
        # 1. Get Post Time (Local)
        created_time = parser.parse(post['created_time']).astimezone()
        hour = created_time.hour
        
        # 2. Get Reach (Traffic)
        reach = 0
        if 'insights' in post:
            for i in post['insights']['data']:
                if i['name'] == 'post_impressions_unique':
                    reach = i['values'][0]['value']
                    break
        
        # Add to bucket
        hourly_counts[hour] += reach

    # Format exactly like the daily output
    formatted_hourly = []
    for h in range(24):
        # Only include hours with data to keep it clean
        if hourly_counts[h] > 0:
            formatted_hourly.append({
                "hour": f"{h:02d}:00",
                "views": hourly_counts[h]  # Represents Post Reach
            })
            
    return formatted_hourly

def main():
    print("\n📊 Fetching Facebook Page Traffic...\n")

    try:
        # 1. Daily Page Views (Standard API)
        daily_views = fetch_insights("page_views_total", "day")

        # 2. Hourly Activity (Fixed Logic)
        # We replace the broken call with the post-analysis function
        hourly_views = fetch_hourly_activity()

        output = {
            "page_id": PAGE_ID,
            "generated_at": datetime.now().isoformat(),
            "traffic": {
                "daily": [
                    {
                        "date": item["end_time"][:10],
                        "views": item["value"]
                    }
                    for item in daily_views
                ],
                "hourly": hourly_views 
            }
        }

        with open("page_traffic.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("✅ Traffic data saved to page_traffic.json\n")

        print("📅 DAILY TRAFFIC (Last 7 Days):")
        for d in output["traffic"]["daily"][-7:]:
            print(f"• {d['date']} → {d['views']} views")

        print("\n⏰ HOURLY ACTIVITY (Peak Times based on Content):")
        # Sort by busiest hours for display
        sorted_hours = sorted(output["traffic"]["hourly"], key=lambda x: x['views'], reverse=True)[:5]
        for h in sorted_hours:
            print(f"• {h['hour']} → ~{h['views']} reach")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
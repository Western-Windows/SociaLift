import requests
import json
import pandas as pd
import sys
from dateutil import parser
from datetime import datetime

# Try to import config
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found.")
    sys.exit(1)

class HeatmapGenerator:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v19.0"
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.access_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.post_limit = 100  # Analyzes last 100 posts

    def fetch_posts(self):
        print(f"⏳ Fetching last {self.post_limit} posts for analysis...")
        
        # Fetch creation time + Reach + Engagement
        fields = "created_time,insights.metric(post_impressions_unique,post_engagements)"
        url = f"{self.base_url}/{self.page_id}/posts"
        params = {
            "access_token": self.access_token,
            "fields": fields,
            "limit": self.post_limit
        }
        
        raw_data = []
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "data" not in data:
                return []

            for post in data['data']:
                # Convert to Local Time
                created_time = parser.parse(post['created_time']).astimezone()
                
                # Extract Metrics
                reach = 0
                engagement = 0
                if 'insights' in post:
                    for item in post['insights']['data']:
                        if item['name'] == 'post_impressions_unique':
                            reach = item['values'][0]['value']
                        elif item['name'] == 'page_post_engagements':
                            engagement = item['values'][0]['value']
                
                raw_data.append({
                    "day_index": created_time.weekday(), # 0=Monday, 6=Sunday
                    "day_name": created_time.strftime('%A'),
                    "hour": created_time.hour, # 0-23
                    "hour_label": created_time.strftime('%H:00'),
                    "reach": reach,
                    "engagement": engagement
                })
                
            return raw_data

        except Exception as e:
            print(f"❌ API Error: {e}")
            return []

    def generate_matrix(self, raw_data):
        if not raw_data: return None

        print("🔄 Processing 7x24 Matrix...")
        df = pd.DataFrame(raw_data)

        # 1. Group by Day and Hour -> Calculate Averages
        grouped = df.groupby(['day_index', 'day_name', 'hour'])[['reach', 'engagement']].mean().reset_index()
        
        # Round values for cleaner display
        grouped['reach'] = grouped['reach'].round(0).astype(int)
        grouped['engagement'] = grouped['engagement'].round(0).astype(int)

        # 2. Format the values into a single string "Reach/Eng" for the table cell
        grouped['cell_value'] = grouped.apply(
            lambda x: f"{x['reach']}/{x['engagement']}", axis=1
        )

        # 3. Create the Matrix (Pivot Table)
        matrix = grouped.pivot(index='day_name', columns='hour', values='cell_value')

        # 4. Reindex to ensure all 7 days and 24 hours exist
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        matrix = matrix.reindex(days_order)
        
        # Ensure all 24 columns exist
        for h in range(24):
            if h not in matrix.columns:
                matrix[h] = "0/0"
        
        matrix = matrix[sorted(matrix.columns)]
        matrix = matrix.fillna("0/0")

        return matrix, grouped

    def export_to_text_file(self, matrix, filename="weekly_heatmap_matrix.txt"):
        print(f"💾 Writing Text Matrix to {filename}...")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("FACEBOOK PAGE HEATMAP (7 Days x 24 Hours)\n")
            f.write("Format: Avg Reach / Avg Engagement\n")
            f.write("=" * 150 + "\n\n")

            header = "Day".ljust(12) + " | ".join([f"{str(h).zfill(2)}:00".center(11) for h in range(24)])
            f.write(header + "\n")
            f.write("-" * len(header) + "\n")

            for day_name, row in matrix.iterrows():
                row_str = " | ".join([str(val).center(11) for val in row])
                line = f"{day_name.ljust(12)} | {row_str}\n"
                f.write(line)
                f.write("-" * len(header) + "\n")
            
            f.write("\n" + "=" * 150 + "\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    def export_to_json(self, grouped_df, raw_count, filename="best_posting_times.json"):
        print(f"💾 Writing JSON Analysis to {filename}...")
        
        # 1. Top Reach Times
        top_reach = grouped_df.sort_values(by='reach', ascending=False).head(5).to_dict('records')
        
        # 2. Top Engagement Times
        top_engagement = grouped_df.sort_values(by='engagement', ascending=False).head(5).to_dict('records')

        # 3. All Slots Data (Flattened list for frontend/charts)
        all_slots = []
        for index, row in grouped_df.iterrows():
            all_slots.append({
                "day": row['day_name'],
                "hour": f"{row['hour']:02d}:00",
                "avg_reach": int(row['reach']),
                "avg_engagement": int(row['engagement'])
            })

        output = {
            "meta": {
                "analyzed_posts": raw_count,
                "generated_at": datetime.now().isoformat()
            },
            "best_times_for_reach": top_reach,
            "best_times_for_engagement": top_engagement,
            "all_slots_data": all_slots
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    generator = HeatmapGenerator()
    
    # 1. Fetch
    raw_data = generator.fetch_posts()
    
    if raw_data:
        # 2. Process
        matrix_df, grouped_df = generator.generate_matrix(raw_data)
        
        # 3. Export Text Table
        generator.export_to_text_file(matrix_df)
        
        # 4. Export JSON Analysis
        generator.export_to_json(grouped_df, len(raw_data))
        
        print("\n✅ All exports complete!")
    else:
        print("⚠️ No data found to generate matrix.")
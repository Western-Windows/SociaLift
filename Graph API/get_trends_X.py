import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
import sys
from deep_translator import GoogleTranslator
from transformers import pipeline

class SmartTrendScraper:
    def __init__(self):
        print("⏳ Loading AI Model (facebook/bart-large-mnli)...")
        # Load the zero-shot classification model
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.translator = GoogleTranslator(source='auto', target='en')
        print("✅ Model Loaded.")

    def get_trends(self, country="egypt", categories=None):
        """
        Fetches, translates, and classifies trends for a specific country 
        using a custom list of categories.
        """
        
        # Default categories if none provided
        if categories is None:
            categories = [
                "Sports", "Politics", "Technology", "Entertainment", 
                "Business", "Health", "Social Issues", "Music"
            ]

        # 1. Construct URL based on country
        country_slug = country.lower().replace(" ", "-")
        if country_slug in ["worldwide", "global"]:
            url = "https://trends24.in/"
        else:
            url = f"https://trends24.in/{country_slug}/"

        print(f"\n🔍 Fetching trends for: {country.title()}")
        print(f"🎯 Classification Categories: {categories}")
        print(f"🔗 URL: {url}...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                print(f"❌ Error: Country '{country}' not found on Trends24.")
                return
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Get the latest list (first one)
            trend_cards = soup.select(".trend-card__list")
            if not trend_cards:
                print("⚠️ No trend lists found.")
                return

            current_trends = trend_cards[0].find_all("li")
            trends_data = []
            
            print(f"🔥 Found {len(current_trends)} trends. Processing...")

            for i, item in enumerate(current_trends, 1):
                link_tag = item.find("a")
                if link_tag:
                    topic_original = link_tag.text.strip()
                    link = link_tag['href']
                    tweet_count = item.find("span", class_="tweet-count").text if item.find("span", class_="tweet-count") else "N/A"

                    # 🅰️ TRANSLATE
                    try:
                        topic_en = self.translator.translate(topic_original)
                        time.sleep(0.1) 
                    except:
                        topic_en = topic_original

                    # 🧠 CLASSIFY (AI) with DYNAMIC CATEGORIES
                    try:
                        ai_result = self.classifier(topic_en, categories, multi_label=False)
                        top_category = ai_result['labels'][0]
                        confidence = ai_result['scores'][0]
                        
                        # Only accept if confidence is decent (>30%), else "General"
                        if confidence < 0.3:
                            top_category = "General/Unsure"
                    except:
                        top_category = "Error"
                        confidence = 0

                    print(f"   🔹 {i}. {topic_original} -> {top_category} ({int(confidence*100)}%)")

                    entry = {
                        "rank": i,
                        "topic_original": topic_original,
                        "topic_english": topic_en,
                        "category": top_category,
                        "confidence": round(confidence, 2),
                        "tweet_count": tweet_count,
                        "url": link
                    }
                    trends_data.append(entry)

            # 💾 Save to JSON
            self.save_results(country, trends_data)

        except Exception as e:
            print(f"❌ Critical Error: {e}")

    def save_results(self, country, data):
        filename = f"trends_{country.lower().replace(' ', '_')}_classified.json"
        
        output = {
            "meta": {
                "country": country,
                "source": "Trends24",
                "timestamp": datetime.datetime.now().isoformat(),
                "total_trends": len(data)
            },
            "trends": data
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Success! Saved to: {filename}")

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    scraper = SmartTrendScraper()
    
    # 1. Define Country
    target_country = "egypt" 
    if len(sys.argv) > 1:
        target_country = sys.argv[1]

    # 2. Define Your Custom Categories Here
    my_custom_categories = [
        "Football", 
        "Economy", 
        "Viral Memes", 
        "TV Shows", 
        "Tech News"
    ]

    # 3. Run with both parameters
    scraper.get_trends(country=target_country, categories=my_custom_categories)
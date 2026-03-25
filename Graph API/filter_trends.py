#!/usr/bin/env python3

"""
Filename: filter_trends.py
Version: 1.0
Description:
This script is designed to filter google trends according to specific categories.
"""

import os
import json
import sys
import warnings
warnings.filterwarnings("ignore")

from transformers import pipeline

PAGE_CATEGORIES = [
    "Technology", 
    "Software", 
    "Gaming", 
    "Business", 
    "Automotive",
    "Sports"
] 

def filter_trends_with_ai():
    print("⏳ Loading AI Model (facebook/bart-large-mnli)...")
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    input_filename = "./Graph API/JSON/top_trends.json" 
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            trends = data.get("top_50_trends", [])
            meta = data.get("meta", {})
            
    except FileNotFoundError:
        print(f"❌ Error: '{input_filename}' not found. Please ensure the file exists.")
        return

    print(f"\n🔍 Analyzing {len(trends)} trends against categories: {PAGE_CATEGORIES}...\n")
    
    relevant_trends = []

    for item in trends:
        trend_text = item.get('topic')
        
        if not trend_text:
            continue

        result = classifier(trend_text, PAGE_CATEGORIES, multi_label=False)
        
        top_category = result['labels'][0]
        top_score = result['scores'][0]

        if top_score > 0.4:
            item['matched_category'] = top_category
            item['ai_confidence'] = f"{int(top_score * 100)}%"
            
            relevant_trends.append(item)
            
        else:
            pass

    output = {
        "meta": meta,
        "filter_settings": {
            "categories_used": PAGE_CATEGORIES,
            "total_scanned": len(trends),
            "relevant_found": len(relevant_trends)
        },
        "filtered_trends": relevant_trends
    }

    output_filename = "./Graph API/JSON/filtered_google_trends.json"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Done! Saved {len(relevant_trends)} relevant trends to '{output_filename}'.")

if __name__ == "__main__":
    filter_trends_with_ai()
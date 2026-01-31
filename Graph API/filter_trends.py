#!/usr/bin/env python3
"""
Smart Trend Filter (Zero-Shot AI) - v2
1. Loads trends from 'clean_trends_report.json' (or your specific file).
2. Extracts 'trend_keyword' from the 'top_50_trends' list.
3. Filters them based on YOUR Page's specific categories.
"""

import json
import sys
import warnings
# Suppress warnings from transformers
warnings.filterwarnings("ignore")

from transformers import pipeline

# 1. Define your Page Categories
# Change these to match your actual Facebook Page categories
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
    
    # Initialize the Zero-Shot Classifier
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # 2. Load the JSON file
    # Ensure this filename matches the one you saved earlier
    input_filename = "top_trends.json" 
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 🔧 CHANGE: Access the specific key from your new structure
            trends = data.get("top_50_trends", [])
            meta = data.get("meta", {})
            
    except FileNotFoundError:
        print(f"❌ Error: '{input_filename}' not found. Please ensure the file exists.")
        return

    print(f"\n🔍 Analyzing {len(trends)} trends against categories: {PAGE_CATEGORIES}...\n")
    
    relevant_trends = []

    for item in trends:
        # 3. CRITICAL CHANGE: Use 'topic' from your new JSON structure
        trend_text = item.get('topic')
        
        if not trend_text:
            continue

        # Ask AI: "Which category does this topic belong to?"
        # Note: Since some keywords are non-English, confidence might vary, 
        # but BART handles mixed text reasonably well for broad categories.
        result = classifier(trend_text, PAGE_CATEGORIES, multi_label=False)
        
        top_category = result['labels'][0]
        top_score = result['scores'][0]

        # Threshold: If AI is > 40% sure it matches a category
        if top_score > 0.4:
            # Add classification data to the item
            item['matched_category'] = top_category
            item['ai_confidence'] = f"{int(top_score * 100)}%"
            
            relevant_trends.append(item)
            
            print(f"   ✅ MATCH: '{trend_text}' -> {top_category} [{item['ai_confidence']}]")
        else:
            # Optional: Print drops to see what's being ignored
            # print(f"   ❌ DROP: '{trend_text}' ({top_category} - {int(top_score*100)}%)")
            pass

    # Save Filtered Results preserving metadata
    output = {
        "meta": meta,
        "filter_settings": {
            "categories_used": PAGE_CATEGORIES,
            "total_scanned": len(trends),
            "relevant_found": len(relevant_trends)
        },
        "filtered_trends": relevant_trends
    }

    output_filename = "filtered_trends_final.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Done! Saved {len(relevant_trends)} relevant trends to '{output_filename}'.")

if __name__ == "__main__":
    filter_trends_with_ai()
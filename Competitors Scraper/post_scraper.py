
"""
Post Scraper Module - Refactored for pipeline use
"""

import re
import time
import random
import json
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fb_graphql_scraper.facebook_graphql_scraper import FacebookGraphqlScraper
from fb_graphql_scraper.utils import utils as fb_utils
import fb_graphql_scraper.facebook_graphql_scraper as fb_scraper_module


# ================= LIBRARY FIXES =================
_original_days_difference = fb_utils.days_difference_from_now

def _safe_days_difference(tmp_creation_array: list) -> int:
    if not tmp_creation_array:
        return 0
    return _original_days_difference(tmp_creation_array)

fb_utils.days_difference_from_now = _safe_days_difference
fb_scraper_module.days_difference_from_now = _safe_days_difference


# ================= DATE PARSER =================
def parse_friendly_date(date_str):
    """
    Converts Facebook text dates into real datetime objects.
    Handles: "2 hrs", "Yesterday at 5:00 PM", "2 February at 18:47"
    """
    if not isinstance(date_str, str):
        return None
    
    now = datetime.now()
    clean_str = date_str.lower().strip()

    try:
        # Case 1: "Just now", "mins", "hrs" -> Today
        if any(x in clean_str for x in ['just now', 'min', 'hr', 'now']):
            return now

        # Case 2: "Yesterday at..."
        if "yesterday" in clean_str:
            return now - timedelta(days=1)

        # Case 3: "2 February at 18:47"
        match = re.search(r"(\d+)\s+([a-zA-Z]+).*?at\s+(\d{1,2}:\d{2})", date_str)
        if match:
            day, month_str, time_str = match.groups()
            year = now.year
            full_str = f"{day} {month_str} {year} {time_str}"
            return datetime.strptime(full_str, "%d %B %Y %H:%M")
            
    except Exception:
        pass
    
    return None


# ================= LOGIN FUNCTIONS =================
def human_type(element, text):
    """Type like a human to avoid detection"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))


def perform_login(driver, email, password):
    """
    Perform Facebook login (reusable function)
    Returns: True if successful, False otherwise
    """
    print("\n🔑 Logging in to Facebook...")
    try:
        driver.get("https://www.facebook.com/")
        time.sleep(random.uniform(3, 5))

        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        time.sleep(1)
        email_field.click()
        human_type(email_field, email)
        
        pass_field = driver.find_element(By.NAME, "pass")
        pass_field.click()
        human_type(pass_field, password)
        time.sleep(1)
        pass_field.send_keys(Keys.ENTER)
        
        print("   Waiting for login to complete...")
        time.sleep(10)
        print("   ✅ Login successful")
        return True
    except Exception as e:
        print(f"   ⚠️ Login failed: {e}")
        return False


# ================= POST SCRAPING =================
def scrape_page_posts(scraper, page_identifier, days_back=10):
    """
    Scrape posts from a single Facebook page
    
    Args:
        scraper: FacebookGraphqlScraper instance (already logged in)
        page_identifier: Facebook username or URL
        days_back: Number of days to scrape
        
    Returns:
        List of valid posts with cleaned dates
    """
    # Clean the identifier thoroughly
    page_identifier = str(page_identifier).strip()
    # Remove all protocols and repeated facebook.com/ patterns
    cleaned = page_identifier
    # Remove all protocols
    cleaned = re.sub(r'(https?://)+', '', cleaned)
    # Remove all www.
    cleaned = re.sub(r'(www\.)+', '', cleaned)
    # Find the last occurrence of 'facebook.com/' and take what comes after
    idx = cleaned.rfind('facebook.com/')
    if idx != -1:
        cleaned = cleaned[idx + len('facebook.com/'):]
    # Remove everything after the username (/, ?, etc.)
    username = cleaned.split('/')[0].split('?')[0].strip()
    # Validate username
    if not username or 'facebook.com' in username or 'http' in username:
        print(f"   ❌ Could not extract valid username from: {page_identifier}")
        return []
    # Build clean target URL
    target_page = f"{username}/"
    
    print(f"\n📄 Scraping: {username}")
    print(f"   Target: {target_page}")
    
    try:
        # Fetch posts
        data = scraper.get_user_posts(
            target_page, 
            days_limit=days_back + 10, 
            display_progress=True
        )
        
        posts = data if isinstance(data, list) else data.get('data', [])
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        valid_posts = []
        
        for p in posts:
            raw_date = p.get('published_date2', p.get('published_date'))
            final_date = None
            
            # Parse timestamp
            if isinstance(raw_date, (int, float)) or (isinstance(raw_date, str) and raw_date.replace('.','').isdigit()):
                try:
                    ts = float(raw_date)
                    if ts > 10000000000:
                        ts /= 1000
                    final_date = datetime.fromtimestamp(ts)
                except:
                    pass
            
            # Parse text date
            elif isinstance(raw_date, str):
                final_date = parse_friendly_date(raw_date)
                if not final_date:
                    try:
                        final_date = datetime.fromisoformat(raw_date)
                    except:
                        pass
            
            # Filter by date
            if final_date and final_date >= cutoff_date:
                p['clean_date'] = final_date.strftime('%Y-%m-%d %H:%M')
                p['page_username'] = username  # Use the cleaned username
                valid_posts.append(p)
        
        print(f"   ✅ Found {len(valid_posts)} posts from last {days_back} days")
        return valid_posts
        
    except Exception as e:
        print(f"   ❌ Error scraping {page_identifier}: {e}")
        return []


def process_posts_batch(scraper, page_usernames, days_back=10, output_dir="d:/Graduation Project/SociaLift"):
    """
    Scrape posts from multiple pages using a single login session
    
    Args:
        scraper: FacebookGraphqlScraper instance (already logged in)
        page_usernames: List of Facebook usernames/URLs to scrape
        days_back: Number of days to scrape per page
        output_dir: Directory to save results
        
    Returns:
        Dictionary mapping page_username -> list of posts
    """
    all_results = {}
    
    print(f"\n{'='*60}")
    print(f"📊 Scraping {len(page_usernames)} Facebook pages")
    print(f"{'='*60}")
    
    for i, username in enumerate(page_usernames, 1):
        print(f"\n[{i}/{len(page_usernames)}]", end=" ")
        # Final robust cleaning: ensure only username, never a URL
        cleaned = str(username).strip()
        cleaned = re.sub(r'^(https?://)+', '', cleaned)
        cleaned = re.sub(r'^(www\.)+', '', cleaned)
        idx = cleaned.rfind('facebook.com/')
        if idx != -1:
            cleaned = cleaned[idx + len('facebook.com/'):]
        cleaned = cleaned.split('/')[0].split('?')[0].strip()
        posts = scrape_page_posts(scraper, cleaned, days_back)
        all_results[cleaned] = posts
        # Rate limiting between pages
        if i < len(page_usernames):
            wait_time = random.uniform(3, 6)
            print(f"   ⏳ Waiting {wait_time:.1f}s before next page...")
            time.sleep(wait_time)
    
    return all_results


def save_results(all_results, output_dir="d:/Graduation Project/SociaLift"):
    """
    Save scraping results to JSON files
    
    Args:
        all_results: Dictionary mapping page_username -> posts
        output_dir: Directory to save files
        
    Returns:
        List of saved file paths
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save individual page files
    for username, posts in all_results.items():
        if posts:
            safe_name = username.replace('/', '_').replace(':', '').replace('https', '').replace('www.facebook.com', '')
            filename = f"{safe_name}_posts_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({'data': posts, 'page': username, 'scraped_at': timestamp}, f, indent=2, default=str)
            
            saved_files.append(filepath)
            print(f"   💾 Saved: {filename}")
    
    # Save combined results
    combined_file = os.path.join(output_dir, f"all_posts_{timestamp}.json")
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump({
            'scraped_at': timestamp,
            'total_pages': len(all_results),
            'total_posts': sum(len(posts) for posts in all_results.values()),
            'results': all_results
        }, f, indent=2, default=str)
    
    saved_files.append(combined_file)
    print(f"\n   💾 Combined results: all_posts_{timestamp}.json")
    
    return saved_files


from playwright.sync_api import sync_playwright
import time
import os

"""
Filename: get_followers_demographics.py
Version: 1.0
Description:
This script is designed to scrape the followers' demographics data from Facebook pages.
"""

DOWNLOAD_DIR = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Facebook Page credentials must be provided via environment variables for security.
# Set FB_EMAIL and FB_PASSWORD in your environment before running this script.
EMAIL = os.environ.get("FB_EMAIL")
PASSWORD = os.environ.get("FB_PASSWORD")


PAGES = {
    "Emergenhelp": "102446321938796", 
    "Western Windows": "803563356170307",
}

def perform_login(page, location_name):
    """Fills in the login form."""
    print(f"   action: Filling credentials for {location_name}...")
    try:
        page.wait_for_selector('input[name="email"]', state="visible", timeout=5000)
    except:
        return False

    page.click('input[name="email"]')
    time.sleep(0.5)
    page.type('input[name="email"]', EMAIL, delay=100)
    
    page.click('input[name="pass"]')
    time.sleep(0.5)
    page.type('input[name="pass"]', PASSWORD, delay=100)
    
    if page.locator('button[name="login"]').is_visible():
        page.click('button[name="login"]')
    elif page.locator('button[id="loginbutton"]').is_visible():
        page.click('button[id="loginbutton"]')
    
    return True

def process_page(page, page_name, asset_id):
    """Navigates directly to the asset URL and exports."""
    
    target_url = f"https://business.facebook.com/latest/insights/people?asset_id={asset_id}&audience_tab=demographics"
    
    print(f"\n🔹 Processing: {page_name} (ID: {asset_id})")
    print(f"   Navigating directly to: {target_url}")
    
    page.goto(target_url)
    page.wait_for_load_state("networkidle")
    time.sleep(4)

    try:

        if page.locator('text="Select a business asset"').is_visible():
            print("   ❌ Error: Asset ID seems invalid or not accessible.")
            return

        export_btn = page.locator('div[role="button"]:has-text("Export")').first
        
        if export_btn.is_visible():
            export_btn.click()
            print("   Clicked Export...")
            
            csv_option = page.locator('div[role="menuitem"]:has-text("CSV")')
            csv_option.wait_for(state="visible", timeout=5000)
            
            with page.expect_download() as download_info:
                csv_option.click()
            
            download = download_info.value
            save_path = os.path.join(DOWNLOAD_DIR, f"{page_name}_demographics.csv")
            download.save_as(save_path)
            print(f"   ✅ SUCCESS: Saved to {save_path}")
        else:
            print("   ❌ Export button not found (Check 100 followers rule).")

    except Exception as e:
        print(f"   ❌ Failed to export {page_name}: {e}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context(viewport={'width': 1600, 'height': 900}, accept_downloads=True)
    page = context.new_page()
    print("🔹 Step 1: Login...")
    page.goto("https://www.facebook.com/login")
    
    try:
        page.get_by_role("button", name="Allow all cookies").click(timeout=3000)
    except:
        pass

    perform_login(page, "Initial Page")
    
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except:
        pass

    first_page_name = list(PAGES.keys())[0]
    first_page_id = list(PAGES.values())[0]
    temp_url = f"https://business.facebook.com/latest/insights/people?asset_id={first_page_id}"
    
    page.goto(temp_url)
    page.wait_for_load_state("networkidle")
    if page.locator('text="Log in to Business Tools"').is_visible() or page.locator('text="Get started with business tools"').is_visible():
        page.click('div[role="button"]:has-text("Log in with Facebook"), span:has-text("Log in with Facebook")')
        time.sleep(3) 
        if page.locator('input[name="pass"]').is_visible():
            perform_login(page, "Popup Modal")
            page.wait_for_load_state("networkidle")
            time.sleep(5)
    for name, asset_id in PAGES.items():
        process_page(page, name, asset_id)
        time.sleep(2)

    print("\n🏁 All pages processed.")
    browser.close()
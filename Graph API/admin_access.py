import os

from playwright.sync_api import sync_playwright
import time

"""
Filename: admin_access.py
Version: 1.0
Description:
This script is designed to automate the process of accepting admin invites for Facebook Pages.
"""

# Must be updated with SociaLift's Facebook Page credentials
EMAIL = os.environ.get("FB_EMAIL")
PASSWORD = os.environ.get("FB_PASSWORD")


def perform_login(page, location_name):
    """Fills in the login form. Works for both the main page and popups."""
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

def handle_splash_page(page):
    """Handles the 'Get started with business tools' page."""
    if page.locator('text="Log in to Business Tools"').is_visible() or \
       page.locator('text="Get started with business tools"').is_visible():
        
        print("ℹ️  Stuck on Business Tools splash page. Clicking 'Log in with Facebook'...")
        page.click('div[role="button"]:has-text("Log in with Facebook"), span:has-text("Log in with Facebook")')
        time.sleep(3) 

        if page.locator('input[name="pass"]').is_visible():
            print("🚨 Re-authentication popup detected. Entering password...")
            perform_login(page, "Popup Modal")
            page.wait_for_load_state("networkidle")

def accept_admin_invites(page):
    print("\n🔹 Checking for Pending Invites...")
   
    page.goto("https://www.facebook.com/pages/?category=invites")
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except: pass
    
    time.sleep(3) 

    try:
        accept_buttons = page.locator('div[role="button"]:has-text("Accept")')
        count = accept_buttons.count()

        if count == 0:
            print("✅ No pending invites found.")
            return

        print(f"🔹 Found {count} invite(s). Processing...")

        for i in range(count):

            btn = page.locator('div[role="button"]:has-text("Accept")').first
            if btn.is_visible():
                btn.click()
                print("   Clicked 'Accept'...")
                time.sleep(2)

                try:
                    modal_accept = page.locator('div[role="dialog"] div[role="button"]:has-text("Accept")')
                    if modal_accept.is_visible():
                        modal_accept.click()
                        print("   Confirmed in popup.")
                        time.sleep(3)

                    if page.locator('input[name="pass"]').is_visible():
                        print("   🚨 Password requested for confirmation...")
                        perform_login(page, "Confirmation Modal")
                        time.sleep(3)
                
                except:
                    print("   (No confirmation popup appeared, moving on...)")

            time.sleep(2)
            
        print("✅ All invites processed.")

    except Exception as e:
        print(f"❌ Error while accepting invites: {e}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()

    print("🔹 Step 1: Login...")
    page.goto("https://www.facebook.com/login")
    try: page.get_by_role("button", name="Allow all cookies").click(timeout=3000)
    except: pass

    perform_login(page, "Initial Page")
    try: page.wait_for_load_state("networkidle", timeout=10000)
    except: pass

    print("🔹 Checking for Business Suite redirect...")
    page.goto("https://business.facebook.com/overview")
    time.sleep(3)
    handle_splash_page(page)
    accept_admin_invites(page)

    time.sleep(5)
    browser.close()
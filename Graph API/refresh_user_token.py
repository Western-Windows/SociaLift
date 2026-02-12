import requests
import os
import sys
from dotenv import load_dotenv, set_key


"""
Filename: refresh_user_token.py
Version: 1.0
Description:
This script is designed to automatically renew Facebook user access tokens.
"""

env_file = "Graph API/.env"
if not os.path.exists(env_file):
    env_file = ".env" 
load_dotenv(env_file)

APP_ID = os.getenv("FACEBOOK_APP_ID")
APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
OLD_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

def auto_renew_token():
    print("🔄 Checking Token Validity & Auto-Extending...")

    if not all([APP_ID, APP_SECRET, OLD_TOKEN]):
        print("❌ Error: Missing credentials in .env file.")
        return

    url = "https://graph.facebook.com/v24.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": OLD_TOKEN
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "access_token" in data:
            new_long_token = data["access_token"]
            expires_seconds = data.get("expires_in", 0)
            days_left = int(expires_seconds) / 86400

            print(f"✅ Success! Token extended.")
            print(f"   📅 New Validity: ~{days_left:.1f} days")

            set_key(
                dotenv_path=env_file, 
                key_to_set="FACEBOOK_ACCESS_TOKEN", 
                value_to_set=new_long_token, 
                quote_mode="never" 
            )
            print(f"   💾 Updated .env file with new token ")

        else:
            error = data.get("error", {})
            print(f"❌ Failed to extend token.")
            print(f"   Reason: {error.get('message')}")
            print(f"   Code: {error.get('code')}")
            
            if error.get('code') == 190:
                print("\n⚠️ CRITICAL: Your token is EXPIRED.")
                print("   You strictly cannot regenerate an expired User Token via script.")
                print("   You MUST generate a fresh token manually from Graph API Explorer.")

    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    auto_renew_token()
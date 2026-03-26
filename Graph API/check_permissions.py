#!/usr/bin/env python3

"""
Filename: check_permissions.py
Version: 1.10
Description:
This script checks and verifies Facebook user and page access tokens permissions,
also validates page posting capabilities.
"""

import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import Config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class FacebookAuthManager:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v24.0"
        self.user_token = Config.FACEBOOK_ACCESS_TOKEN
        self.page_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.session = self._create_session()

    def _create_session(self):
        """Creates a session with exponential backoff retries for 429, 500, 502, 503, 504."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _api_call(self, method, endpoint, token, params=None, data=None):
        """Generic helper to handle API requests and error logging."""
        url = f"{self.base_url}/{endpoint}"
        all_params = {"access_token": token}
        if params:
            all_params.update(params)
            
        try:
            response = self.session.request(method, url, params=all_params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"API Error ({endpoint}): {e.response.json().get('error', {}).get('message', e)}")
            return None
        except Exception as e:
            logger.error(f"Connection Error: {e}")
            return None

    def check_user_permissions(self):
        """Validates scopes granted to the User token."""
        data = self._api_call("GET", "me/permissions", self.user_token)
        if not data: return []
        
        granted = [p["permission"] for p in data.get("data", []) if p["status"] == "granted"]
        logger.info(f"User Permissions Granted: {', '.join(granted)}")
        return granted

    def verify_page_access(self):
        """Confirms the Page token can reach the target Page."""
        data = self._api_call("GET", self.page_id, self.page_token, params={"fields": "name"})
        if data:
            logger.info(f"Page Access Verified: {data.get('name')}")
            return True
        return False

    def perform_dry_run_post(self):
        """Executes a real post and immediate deletion to confirm write access."""
        logger.info("Starting dry-run post test...")
        post_data = {"message": "Diagnostic test post (Auto-delete)"}
        
        res = self._api_call("POST", f"{self.page_id}/feed", self.page_token, data=post_data)
        if not res: return False
        
        post_id = res.get("id")
        logger.info(f"Post successful (ID: {post_id}). Cleaning up...")

        self._api_call("DELETE", post_id, self.page_token)
        logger.info("Cleanup complete.")
        return True

    def run_full_diagnostic(self):
        """Orchestrates the full permission check suite."""
        required = {"pages_manage_posts", "pages_read_engagement", "pages_show_list"}
        
        user_perms = set(self.check_user_permissions())
        page_ok = self.verify_page_access()
        
        missing = required - user_perms
        
        print("\n" + "="*30 + "\nDIAGNOSTIC REPORT\n" + "="*30)
        for perm in required:
            status = "✅" if perm in user_perms else "❌"
            print(f"{status} {perm}")
        
        can_post = not missing and page_ok
        if can_post:
            write_test = self.perform_dry_run_post()
            final_status = "READY ✅" if write_test else "WRITE FAILED ❌"
        else:
            final_status = "CONFIG ERROR ❌"
            
        print(f"\nFINAL STATUS: {final_status}\n" + "="*30)

if __name__ == "__main__":
    manager = FacebookAuthManager()
    manager.run_full_diagnostic()
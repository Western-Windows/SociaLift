#!/usr/bin/env python3
import logging
import requests
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Try to import config, else prompt user
try:
    from config import Config
except ImportError:
    print("❌ Error: config.py not found. Please ensure you have the configuration file.")
    sys.exit(1)

# Configure Logger (hidden in interactive mode to keep UI clean, errors still show)
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class FacebookPoster:
    MAX_VIDEO_SIZE_BYTES = 1024 * 1024 * 1024  # 1GB Limit

    def __init__(self):
        self.access_token = Config.FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = Config.FACEBOOK_PAGE_ID
        self.base_url = "https://graph.facebook.com/v24.0"
        
        if not self.access_token or not self.page_id:
            print("❌ Credentials missing. Check .env file.")
            sys.exit(1)

        self.session = requests.Session()

    def _request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, files: Dict = None) -> Dict[str, Any]:
        """Centralized request handler."""
        url = f"{self.base_url}/{endpoint}"
        if params is None: params = {}
        params['access_token'] = self.access_token

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                files=files,
                timeout=60
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_msg = e.response.json().get('error', {}).get('message', str(e))
                except ValueError:
                    error_msg = e.response.text
            
            return {'error': error_msg}

    def _validate_file(self, file_path: str, is_video: bool = False) -> Optional[str]:
        """Checks if file exists and is within size limits."""
        path = Path(file_path)
        if not path.exists():
            return f"File not found: {file_path}"
        
        if is_video:
            size = path.stat().st_size
            if size > self.MAX_VIDEO_SIZE_BYTES:
                return f"Video too large ({size / (1024**3):.2f}GB). Max allowed is 1GB."
        return None

    # --- Posting Methods ---

    def post_text(self, message: str, link: str = None) -> Dict:
        if not message.strip():
            return {'success': False, 'error': 'Message cannot be empty'}

        data = {'message': message}
        if link: data['link'] = link

        result = self._request(f"{self.page_id}/feed", method="POST", data=data)
        
        if 'id' in result:
            return {'success': True, 'post_id': result['id']}
        return {'success': False, 'error': result.get('error', 'Unknown error')}

    def post_photo(self, photo_path: str, message: str = None) -> Dict:
        error = self._validate_file(photo_path)
        if error: return {'success': False, 'error': error}

        data = {'published': 'true'}
        if message: data['message'] = message

        with open(photo_path, 'rb') as f:
            result = self._request(f"{self.page_id}/photos", method="POST", data=data, files={'source': f})
            
        if 'id' in result:
            return {'success': True, 'post_id': result['id']}
        return {'success': False, 'error': result.get('error', 'Unknown error')}

    def post_video(self, video_path: str, message: str = None) -> Dict:
        error = self._validate_file(video_path, is_video=True)
        if error: return {'success': False, 'error': error}

        data = {'published': 'true'}
        if message: data['message'] = message

        with open(video_path, 'rb') as f:
            result = self._request(f"{self.page_id}/videos", method="POST", data=data, files={'source': f})

        if 'id' in result:
            return {'success': True, 'post_id': result['id']}
        return {'success': False, 'error': result.get('error', 'Unknown error')}

    # --- Scheduling Methods ---

    def schedule_post(self, message: str, scheduled_time_str: str, link: str = None) -> Dict:
        try:
            dt = datetime.fromisoformat(scheduled_time_str)
            timestamp = int(dt.timestamp())
        except ValueError:
            return {'success': False, 'error': 'Invalid format. Use ISO (YYYY-MM-DDTHH:MM:SS)'}

        now = int(time.time())
        if timestamp < now + 600:
            return {'success': False, 'error': 'Time must be at least 10 mins in the future.'}

        data = {
            'message': message,
            'published': 'false',
            'scheduled_publish_time': timestamp
        }
        if link: data['link'] = link

        result = self._request(f"{self.page_id}/feed", method="POST", data=data)

        if 'id' in result:
            return {'success': True, 'post_id': result['id']}
        return {'success': False, 'error': result.get('error', 'Unknown error')}

    def get_scheduled_posts(self) -> Dict:
        fields = "id,message,scheduled_publish_time,created_time"
        params = {"fields": fields, "limit": 25}
        result = self._request(f"{self.page_id}/scheduled_posts", method="GET", params=params)

        if 'data' in result:
            return {'success': True, 'posts': result['data']}
        return {'success': False, 'error': result.get('error', 'Unknown error')}

# --- Interactive Helper Functions ---

def get_input(prompt: str, required: bool = True) -> str:
    """Helper to get user input cleanly."""
    while True:
        value = input(f"   🔹 {prompt}: ").strip()
        if not required or value:
            return value
        print("      ❌ This field is required. Please try again.")

def print_header():
    print("\n" + "=" * 40)
    print("   🚀 FACEBOOK POSTING TOOL")
    print("=" * 40)

def main():
    poster = FacebookPoster()

    while True:
        print_header()
        print("   1. 📝 Post Text Update")
        print("   2. 📷 Post Photo")
        print("   3. 🎥 Post Video")
        print("   4. 📅 Schedule a Post")
        print("   5. 📋 List Scheduled Posts")
        print("   0. 🚪 Exit")
        print("-" * 40)

        choice = input("   👉 Select an option (0-5): ").strip()
        print()

        if choice == "0":
            print("   👋 Goodbye!")
            sys.exit(0)

        # --- OPTION 1: TEXT ---
        elif choice == "1":
            print("   [Post Text Update]")
            msg = get_input("Enter Message")
            link = get_input("Enter Link (optional)", required=False)
            
            print("   ⏳ Posting...")
            result = poster.post_text(msg, link)
            _print_result(result)

        # --- OPTION 2: PHOTO ---
        elif choice == "2":
            print("   [Post Photo]")
            path = get_input("Enter Photo Path (e.g. image.jpg)")
            msg = get_input("Enter Caption (optional)", required=False)
            
            print("   ⏳ Uploading...")
            result = poster.post_photo(path, msg)
            _print_result(result)

        # --- OPTION 3: VIDEO ---
        elif choice == "3":
            print("   [Post Video]")
            path = get_input("Enter Video Path (e.g. clip.mp4)")
            msg = get_input("Enter Caption (optional)", required=False)
            
            print("   ⏳ Uploading...")
            result = poster.post_video(path, msg)
            _print_result(result)

        # --- OPTION 4: SCHEDULE ---
        elif choice == "4":
            print("   [Schedule Post]")
            msg = get_input("Enter Message")
            time_str = get_input("Enter ISO Time (YYYY-MM-DD HH:MM:SS)")
            link = get_input("Enter Link (optional)", required=False)
            
            print("   ⏳ Scheduling...")
            result = poster.schedule_post(msg, time_str, link)
            _print_result(result)

        # --- OPTION 5: LIST SCHEDULED ---
        elif choice == "5":
            print("   [Scheduled Posts]")
            print("   ⏳ Fetching...")
            result = poster.get_scheduled_posts()
            
            if result['success']:
                posts = result['posts']
                if not posts:
                    print("   📭 No scheduled posts found.")
                else:
                    print(f"\n   ✅ Found {len(posts)} posts:")
                    for p in posts:
                        ts = p.get('scheduled_publish_time', 0)
                        date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                        msg_preview = p.get('message', 'No text')[:40].replace('\n', ' ')
                        print(f"      🕒 {date_str} | ID: {p['id']} | {msg_preview}...")
            else:
                print(f"      ❌ Error: {result.get('error')}")

        else:
            print("   ❌ Invalid choice. Please try again.")
            time.sleep(1)

def _print_result(result):
    if result.get('success'):
        print(f"   ✅ SUCCESS! Post ID: {result.get('post_id')}")
    else:
        print(f"   ❌ FAILED: {result.get('error')}")
    input("\n   Press Enter to return to menu...")

if __name__ == "__main__":
    main()
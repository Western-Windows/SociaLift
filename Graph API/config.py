import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Facebook API Configuration
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
    FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')
    FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')

    # API Endpoints
    FACEBOOK_GRAPH_API_VERSION = 'v24.0'
    FACEBOOK_GRAPH_API_BASE = f'https://graph.facebook.com/{FACEBOOK_GRAPH_API_VERSION}'

    # Analytics Settings
    DEFAULT_DATE_RANGE_DAYS = 30
    METRICS_UPDATE_INTERVAL = 3600  # 1 hour in seconds

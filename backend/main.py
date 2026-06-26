import os
import sys
import datetime
import requests # <--- Add this import
from dotenv import load_dotenv # <--- Add this import
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

load_dotenv()
FB_APP_ID = os.getenv("FACEBOOK_APP_ID")
FB_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
if not FB_APP_ID or not FB_APP_SECRET:
    raise RuntimeError("FB_APP_ID and FB_APP_SECRET must be set in environment variables")

sys.path.insert(0, os.path.dirname(__file__))

import models
import schemas
from database import engine, get_db

# Create the database tables automatically when the app starts
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SociaLift API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173","https://localhost:5173","https://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/api/health")
def health_check():
    return {"status": "Backend is running!"}

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash the password and save to DB
    hashed_pw = get_password_hash(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pw)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/api/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Find the user by email
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    # 2. Verify existence and password match
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    
    # 3. Return the user ID for your temporary frontend session management
    return {
        "message": "Login successful", 
        "user_id": db_user.id,
        "username": db_user.username
    }


# --- NEW: FACEBOOK AUTHENTICATION ENDPOINT ---

@app.post("/api/auth/facebook")
def facebook_login(payload: schemas.FacebookLoginRequest, db: Session = Depends(get_db)):
    short_lived_token = payload.accessToken

    # 1. Verify the incoming token with Facebook Graph API
    debug_url = f"https://graph.facebook.com/debug_token?input_token={short_lived_token}&access_token={FB_APP_ID}|{FB_APP_SECRET}"
    debug_response = requests.get(debug_url).json()
    
    token_data = debug_response.get("data", {})
    if not token_data.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired Facebook access token"
        )
    
    fb_user_id = token_data.get("user_id")

    # 2. Exchange the short-lived token for a long-lived token (60 days)
    exchange_url = (
        f"https://graph.facebook.com/v19.0/oauth/access_token?"
        f"grant_type=fb_exchange_token&client_id={FB_APP_ID}&"
        f"client_secret={FB_APP_SECRET}&fb_exchange_token={short_lived_token}"
    )
    exchange_response = requests.get(exchange_url).json()
    long_lived_token = exchange_response.get("access_token")
    
    if not long_lived_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to obtain long-lived access token from Facebook"
        )

    # ... [Previous code getting the long_lived_token] ...

    # 1. Fetch user profile data
    profile_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={long_lived_token}"
    profile_response = requests.get(profile_url).json()
    email = profile_response.get("email")
    username = profile_response.get("name")
    fb_user_id = profile_response.get("id")

    # 2. Fetch the User's Pages and their specific PAGE ACCESS TOKENS
    pages_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={long_lived_token}"
    pages_response = requests.get(pages_url).json()
    
    # For simplicity, we grab the first page the user manages. 
    # (Later you can return a list to React and let the user pick one)
    page_id = None
    page_token = None
    if "data" in pages_response and len(pages_response["data"]) > 0:
        first_page = pages_response["data"][0]
        page_id = first_page.get("id")
        page_token = first_page.get("access_token")

    # 3. Save EVERYTHING to the database
    user = db.query(models.User).filter(models.User.facebook_id == fb_user_id).first()
    
    if not user:
        if email:
            user = db.query(models.User).filter(models.User.email == email).first()
        
        if user:
            user.facebook_id = fb_user_id
            user.fb_access_token = long_lived_token
            user.fb_page_id = page_id
            user.fb_page_access_token = page_token
        else:
            user = models.User(
                username=username,
                email=email if email else f"{fb_user_id}@facebook.local",
                facebook_id=fb_user_id,
                fb_access_token=long_lived_token,
                fb_page_id=page_id,
                fb_page_access_token=page_token
            )
            db.add(user)
    else:
        # Update tokens on returning login
        user.fb_user_access_token = long_lived_token
        user.fb_page_id = page_id
        user.fb_page_access_token = page_token

    db.commit()
    db.refresh(user)

    return {
        "message": "Facebook login & Page link successful",
        "user_id": user.id,
        "linked_page_id": user.fb_page_id
    }


# Import your existing scripts
from Graph.facebook_posting import FacebookPoster
from Graph.get_page_insights import PageInsightsFetcher

# --- POST GENERATION ENDPOINT ---

@app.post("/api/posts/schedule")
def schedule_facebook_post(request: schemas.ScheduleRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    
    if not user or not user.fb_page_access_token:
        raise HTTPException(status_code=400, detail="Facebook Page not connected")
        
    page_id = user.fb_page_id 
    poster = FacebookPoster(access_token=user.fb_page_access_token, page_id=page_id)
    
    # 1. Schedule via Facebook Graph API
    result = poster.schedule_post(
        message=request.message, 
        scheduled_time_str=request.scheduled_time_str
    )
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
        
    # 2. NEW: Save a local record for the Calendar Dashboard
    new_post = models.ScheduledPost(
        user_id=user.id,
        message=request.message,
        scheduled_time_str=request.scheduled_time_str,
        fb_post_id=result.get('post_id')
    )
    db.add(new_post)
    db.commit()
    
    return {"message": "Post scheduled successfully!", "post_id": result.get('post_id')}


# --- DASHBOARD ENDPOINT ---

@app.get("/api/dashboard/insights")
def get_dashboard_insights(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user or not user.fb_access_token:
        raise HTTPException(status_code=400, detail="Facebook not connected")
    
    page_id = user.fb_page_id
    fetcher = PageInsightsFetcher(access_token=user.fb_access_token, page_id=page_id)
    
    daily_raw = fetcher.fetch_insights(days_ago=30)
    fb_data = fetcher.group_and_aggregate(daily_raw) if daily_raw else {}
    
    # 1. Prepare your standard chart data (Visitor, Reactions, etc.)
    visitor_data_formatted = fb_data.get("visitors", []) 
    reaction_types_formatted = fb_data.get("reactions", [])
    engagement_formatted = fb_data.get("engagement", [])
    # ... (Keep your existing formatting logic here) ...
    visitor_data_formatted = [] # Your existing mappings
    reaction_types_formatted = [] 
    engagement_formatted = []

    # --- NEW WAREHOUSE B: Fetch Scheduled Posts DIRECTLY from Facebook ---
    calendar_events = []
    
    # STEP 1: Trade the User Token for the Page Token
    accounts_url = "https://graph.facebook.com/v19.0/me/accounts"
    accounts_params = {"access_token": user.fb_access_token}
    accounts_response = requests.get(accounts_url, params=accounts_params)
    
    page_access_token = None
    
    if accounts_response.status_code == 200:
        pages_data = accounts_response.json().get("data", [])
        # Loop through the pages this user manages to find the matching token
        for page in pages_data:
            if page.get("id") == page_id:
                page_access_token = page.get("access_token")
                break

    if not page_access_token:
        print(f"Error: Could not find a Page Access Token for page {page_id}.")
    else:
        # STEP 2: Now ask for the scheduled posts using the PAGE Token!
        url = f"https://graph.facebook.com/v19.0/{page_id}/scheduled_posts"
        params = {
            "fields": "id,message,scheduled_publish_time",
            "access_token": page_access_token # <--- This is the magic key
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            fb_scheduled_posts = response.json().get("data", [])
            
            for post in fb_scheduled_posts:
                try:
                    unix_time = post.get("scheduled_publish_time")
                    message = post.get("message", "No caption")
                    
                    dt_obj = datetime.datetime.fromtimestamp(unix_time)
                    
                    calendar_events.append({
                        "date": dt_obj.strftime("%Y-%m-%d"),
                        "time": dt_obj.strftime("%H:%M"),
                        "title": message[:15] + ("..." if len(message) > 15 else ""),
                        "color": "blue" 
                    })
                except Exception as e:
                    print(f"Failed to parse Facebook scheduled post: {e}")
        else:
            print(f"Error fetching scheduled posts: {response.text}")

    # --- THE DELIVERY: Send it all to React ---
    return {
        "data": {
            "visitorData": visitor_data_formatted,
            "reactionTypes": reaction_types_formatted, 
            "engagementData": engagement_formatted,
            "calendarEvents": calendar_events 
        }
    }
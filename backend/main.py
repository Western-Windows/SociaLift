import os
import sys
import datetime
import requests # <--- Add this import
from dotenv import load_dotenv # <--- Add this import
from fastapi import FastAPI, Depends, HTTPException, logger, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import bcrypt

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

# Password hashing setup using bcrypt natively
def get_password_hash(password: str):
    # Truncate to 72 characters to prevent bcrypt 72-byte limit crashes
    print("Password: ", password)
    truncated_password = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(truncated_password, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    if not hashed_password:
        return False
    try:
        # We must also truncate the plain text password during login to match the hash
        truncated_password = plain_password[:72].encode('utf-8')
        return bcrypt.checkpw(truncated_password, hashed_password.encode('utf-8'))
    except Exception:
        return False

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
    print("BACKEND RECEIVED PASSWORD:", repr(user.password))
    print("PASSWORD LENGTH:", len(user.password))
    # 2. Hash the password and save to DB
    hashed_pw = get_password_hash(user.password)
    print("HASHED PASSWORD:", repr(hashed_pw))
    print("HASHED LENGTH:", len(hashed_pw))
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
    fb_email = profile_response.get("email")
    fb_username = profile_response.get("name")
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
        if payload.is_signup:
            if not payload.username or not payload.email or not payload.password:
                raise HTTPException(status_code=400, detail="Username, email, and password are required for signup")
            
            # Check if email already exists
            user = db.query(models.User).filter(models.User.email == payload.email).first()
            if user:
                user.facebook_id = fb_user_id
                user.fb_access_token = long_lived_token
                user.fb_page_id = page_id
                user.fb_page_access_token = page_token
            else:
                hashed_pw = get_password_hash(payload.password)
                user = models.User(
                    username=payload.username,
                    email=payload.email,
                    hashed_password=hashed_pw,
                    facebook_id=fb_user_id,
                    fb_access_token=long_lived_token,
                    fb_page_id=page_id,
                    fb_page_access_token=page_token
                )
                db.add(user)
        else:
            if fb_email:
                user = db.query(models.User).filter(models.User.email == fb_email).first()
                if user:
                    user.facebook_id = fb_user_id
                    user.fb_access_token = long_lived_token
                    user.fb_page_id = page_id
                    user.fb_page_access_token = page_token
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, 
                        detail="User not found. Please sign up first."
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="User not found. Please sign up first."
                )
    else:
        # Update tokens on returning login
        user.fb_access_token = long_lived_token
        user.fb_page_id = page_id
        user.fb_page_access_token = page_token

    db.commit()
    db.refresh(user)

    return {
        "message": "Facebook login & Page link successful",
        "user_id": user.id,
        "username": user.username,
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

# --- DASHBOARD ENDPOINT ---

@app.get("/api/dashboard/insights")
def get_dashboard_insights(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user or not user.fb_access_token:
        raise HTTPException(status_code=400, detail="Facebook not connected")
    
    page_id = user.fb_page_id
    fetcher = PageInsightsFetcher(access_token=user.fb_access_token, page_id=page_id)
    
    daily_raw = fetcher.fetch_insights(days_ago=60) # Increased to 60 to get last month data for comparison
    print("RAW DATA LENGTH:", len(daily_raw))
    if len(daily_raw) > 0:
        print("SAMPLE RAW DATA:", daily_raw[0:3]) # Print the first 3 records
    else:
        print("FACEBOOK RETURNED NOTHING.")
    fb_data = fetcher.group_and_aggregate(daily_raw) if daily_raw else []
    
    # --- 1. FORMATTING WAREHOUSE: Map the list of months to Recharts format ---
    visitor_data_formatted = []
    engagement_formatted = []
    follows_formatted = []
    unfollows_formatted = []
    
    for i, month_data in enumerate(fb_data):
        # Format the month string for the X-Axis (e.g., "2024-05" -> "May")
        raw_month = month_data.get("month", "")
        if raw_month:
            dt = datetime.datetime.strptime(raw_month, "%Y-%m")
            month_label = dt.strftime("%b") # Outputs 'Jan', 'Feb', etc.
        else:
            month_label = f"M{i}"

        # A. Mapping Visitor Data (Area Chart)
        visitor_data_formatted.append({
            "name": month_label,
            "impressions": month_data.get("page_impressions_unique", {}).get("value", 0),
            "mediaViews": month_data.get("page_media_view", {}).get("value", 0),
            "postReactions": month_data.get("page_actions_post_reactions_total", {}).get("value", 0)
        })

        # B. Mapping Stat Cards / Sparklines (Compares current index to previous index)
        this_eng = month_data.get("page_post_engagements", {}).get("value", 0)
        last_eng = fb_data[i - 1].get("page_post_engagements", {}).get("value", 0) if i > 0 else 0
        engagement_formatted.append({"week": month_label, "thisMonth": this_eng, "lastMonth": last_eng})

        this_fol = month_data.get("page_daily_follows", {}).get("value", 0)
        last_fol = fb_data[i - 1].get("page_daily_follows", {}).get("value", 0) if i > 0 else 0
        follows_formatted.append({"week": month_label, "thisMonth": this_fol, "lastMonth": last_fol})

        this_unf = month_data.get("page_daily_unfollows_unique", {}).get("value", 0)
        last_unf = fb_data[i - 1].get("page_daily_unfollows_unique", {}).get("value", 0) if i > 0 else 0
        unfollows_formatted.append({"week": month_label, "thisMonth": this_unf, "lastMonth": last_unf})

    # C. Mapping Total Reactions Pie Chart (Summing across all fetched months)
    total_like = sum(m.get("page_actions_post_reactions_like_total", {}).get("value", 0) for m in fb_data)
    total_love = sum(m.get("page_actions_post_reactions_love_total", {}).get("value", 0) for m in fb_data)
    total_haha = sum(m.get("page_actions_post_reactions_haha_total", {}).get("value", 0) for m in fb_data)
    total_wow = sum(m.get("page_actions_post_reactions_wow_total", {}).get("value", 0) for m in fb_data)
    total_sad = sum(m.get("page_actions_post_reactions_sorry_total", {}).get("value", 0) for m in fb_data)
    total_angry = sum(m.get("page_actions_post_reactions_anger_total", {}).get("value", 0) for m in fb_data)

    total_reactions = total_like + total_love + total_haha + total_wow + total_sad + total_angry
    reaction_types_formatted = []

    if total_reactions > 0:
        reaction_types_formatted = [
            {"type": "Like", "percentage": round((total_like / total_reactions) * 100), "color": "#799CE5"},
            {"type": "Love", "percentage": round((total_love / total_reactions) * 100), "color": "#0F2F65"},
            {"type": "Haha", "percentage": round((total_haha / total_reactions) * 100), "color": "#E687D8"},
            {"type": "Wow", "percentage": round((total_wow / total_reactions) * 100), "color": "#39B8FF"},
            {"type": "Sad", "percentage": round((total_sad / total_reactions) * 100), "color": "#CBD5E1"},
            {"type": "Angry", "percentage": round((total_angry / total_reactions) * 100), "color": "#FF4B4B"},
        ]
        # Filter out 0% reactions to keep the pie chart clean
        reaction_types_formatted = [r for r in reaction_types_formatted if r["percentage"] > 0]


    # --- 2. NEW WAREHOUSE B: Fetch Scheduled Posts DIRECTLY from Facebook ---
    calendar_events = []
    
    accounts_url = "https://graph.facebook.com/v19.0/me/accounts"
    accounts_params = {"access_token": user.fb_access_token}
    accounts_response = requests.get(accounts_url, params=accounts_params)
    
    page_access_token = None
    if accounts_response.status_code == 200:
        pages_data = accounts_response.json().get("data", [])
        for page in pages_data:
            if page.get("id") == page_id:
                page_access_token = page.get("access_token")
                break

    if page_access_token:
        url = f"https://graph.facebook.com/v19.0/{page_id}/scheduled_posts"
        params = {
            "fields": "id,message,scheduled_publish_time",
            "access_token": page_access_token
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

    # --- THE DELIVERY: Send it all to React ---
    return {
        "data": {
            "visitorData": visitor_data_formatted,
            "reactionTypes": reaction_types_formatted, 
            "engagementData": engagement_formatted,
            "followsData": follows_formatted,
            "unfollowsData": unfollows_formatted,
            "calendarEvents": calendar_events 
        }
    }

# --- NEW: Persona Endpoints ---
import sys
from pathlib import Path
import json

PERSONA_MODULE_DIR = Path(__file__).resolve().parent.parent / "Persona Module"
if str(PERSONA_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(PERSONA_MODULE_DIR))

@app.post("/api/persona/generate")
def generate_persona(request: schemas.GeneratePersonaRequest):
    try:
        from Persona.personatone import generate_persona_options
        import os
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY missing from environment")
            
        print("Generating persona options...")
        # Since we use the sample post as the only post context, we pass it as input_text
        persona_options = generate_persona_options(
            audience=request.target_audience,
            input_text=request.sample_post,
            api_key=api_key
        )
        
        # persona_options is a Pydantic model PersonaOptions containing a list of PersonaTone
        return persona_options.model_dump()
        
    except Exception as e:
        logger.error(f"Error generating persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/persona/save")
def save_persona(request: schemas.SavePersonaRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        user.persona_json = json.dumps(request.persona_data, ensure_ascii=False)
        db.commit()
        return {"message": "Persona saved successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))
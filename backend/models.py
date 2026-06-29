from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    
    # Standard Login
    hashed_password = Column(String, nullable=False)
    
    # Facebook Login
    facebook_id = Column(String, unique=True, index=True, nullable=True)
    fb_access_token = Column(String, nullable=True) 

    # --- NEW: Facebook Page Credentials ---
    # To run your bot, posting, and insight scripts
    fb_page_id = Column(String, nullable=True)
    fb_page_access_token = Column(String, nullable=True)
    
    # --- NEW: Persona Data ---
    persona_json = Column(String, nullable=True)
    
    # Flags
    is_active = Column(Boolean, default=True)

class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # Links the post to the user
    message = Column(String)
    scheduled_time_str = Column(String) # Stored as "YYYY-MM-DDTHH:MM:SS"
    fb_post_id = Column(String, nullable=True) # The ID Facebook returns
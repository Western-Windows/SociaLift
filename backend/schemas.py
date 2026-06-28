from pydantic import BaseModel, EmailStr

# What the frontend sends when signing up
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# What the frontend sends when logging in
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# What the backend returns to the frontend (notice we don't send the password back)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True # Allows Pydantic to read SQLAlchemy models

        # Add this to the bottom of backend/schemas.py
from typing import Optional

class FacebookLoginRequest(BaseModel):
    accessToken: str
    is_signup: bool = False
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class ScheduleRequest(BaseModel):
    user_id: int
    message: str
    input_type: str = "idea"  # "idea" or "post"
    scheduled_time_str: Optional[str] = None
    skip_enhancement: bool = False

class GeneratePostRequest(BaseModel):
    user_id: int
    message: str
    input_type: str = "idea"  # "idea" or "post"

class GeneratePersonaRequest(BaseModel):
    target_audience: str
    sample_post: str

class SavePersonaRequest(BaseModel):
    user_id: int
    persona_data: dict
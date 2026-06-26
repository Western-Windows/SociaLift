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
class FacebookLoginRequest(BaseModel):
    accessToken: str

class ScheduleRequest(BaseModel):
    user_id: int
    message: str
    scheduled_time_str: str
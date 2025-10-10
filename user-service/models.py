from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    age: Optional[int] = None
    country: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    age: Optional[int] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None

class AuthUserResponse(BaseModel):
    id: str
    email: str
    name: str
    age: Optional[int] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class GoogleCallbackRequest(BaseModel):
    code: str
    redirect_uri: str

class UserInDB(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # Optional for Google users
    name: str
    age: Optional[int] = None
    country: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    google_id: Optional[str] = None
    auth_provider: str = "email"  # "email" or "google"
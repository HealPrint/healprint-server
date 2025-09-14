from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="HealPrint User Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Simple in-memory storage for MVP
users_db = {}

class UserCreate(BaseModel):
    email: str
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

class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/")
async def root():
    return {"service": "HealPrint User Service", "status": "running"}

@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = f"user_{len(users_db) + 1}"
    users_db[user.email] = {
        "id": user_id,
        "email": user.email,
        "password": user.password,  # In production, hash this
        "name": user.name,
        "age": user.age,
        "country": user.country
    }
    
    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        age=user.age,
        country=user.country
    )

@app.post("/login")
async def login_user(credentials: UserLogin):
    """Login user and return token"""
    if credentials.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = users_db[credentials.email]
    if user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple token for MVP
    token = f"token_{user['id']}"
    return {"access_token": token, "token_type": "bearer"}

@app.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    for user in users_db.values():
        if user["id"] == user_id:
            return UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                age=user["age"],
                country=user["country"]
            )
    
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

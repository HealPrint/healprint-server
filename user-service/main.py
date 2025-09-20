from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import bcrypt
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import requests
import os
from jose import JWTError, jwt

from database import connect_to_mongo, close_mongo_connection, get_database
from models import UserCreate, UserResponse, UserLogin, UserInDB, GoogleAuthRequest

# Lifespan context manager for database connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="HealPrint User Service", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware - simplified approach
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,  # Set to False when using *
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_google_token(token: str):
    """Verify Google ID token and return user info"""
    try:
        # Verify the token with Google
        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
        response.raise_for_status()
        
        user_info = response.json()
        
        # Verify the audience matches our client ID
        if user_info.get("aud") != GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=400, detail="Invalid token audience")
        
        return {
            "google_id": user_info.get("sub"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture")
        }
    except requests.RequestException:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token verification failed: {str(e)}")

def hash_password(password: str) -> str:
    """Hash password using bcrypt for production security"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.get("/")
async def root():
    return {"service": "HealPrint User Service", "status": "running"}

@app.get("/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {"message": "CORS is working!", "timestamp": datetime.utcnow().isoformat()}

@app.post("/auth/google", response_model=UserResponse)
async def google_auth(google_auth: GoogleAuthRequest):
    """Authenticate user with Google OAuth"""
    try:
        print(f"🔧 Google auth request received")
        
        # Verify Google token
        google_user = await verify_google_token(google_auth.token)
        print(f"✅ Google token verified for: {google_user['email']}")
        
        db = get_database()
        if db is None:
            print("❌ Database connection not available")
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        # Check if user exists by Google ID or email
        existing_user = await db.users.find_one({
            "$or": [
                {"google_id": google_user["google_id"]},
                {"email": google_user["email"]}
            ]
        })
        
        if existing_user:
            # Update existing user with Google ID if not already set
            if not existing_user.get("google_id"):
                await db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": {"google_id": google_user["google_id"], "auth_provider": "google"}}
                )
            print(f"✅ Existing user found: {existing_user['email']}")
        else:
            # Create new user
            user_doc = {
                "email": google_user["email"],
                "name": google_user["name"],
                "google_id": google_user["google_id"],
                "auth_provider": "google",
                "created_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user_doc)
            existing_user = await db.users.find_one({"_id": result.inserted_id})
            print(f"✅ New Google user created: {google_user['email']}")
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(existing_user["_id"])}, 
            expires_delta=access_token_expires
        )
        
        return {
            "id": str(existing_user["_id"]),
            "email": existing_user["email"],
            "name": existing_user["name"],
            "age": existing_user.get("age"),
            "country": existing_user.get("country"),
            "created_at": existing_user.get("created_at"),
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in Google auth: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register a new user"""
    try:
        print(f"🔧 Register request received for email: {user.email}")
        
        db = get_database()
        if db is None:
            print("❌ Database connection not available")
            raise HTTPException(status_code=500, detail="Database connection not available")
        
        print("✅ Database connection available")
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            print(f"❌ User already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        print("✅ User email is available")
        
        # Create new user document
        user_doc = {
            "email": user.email,
            "password": hash_password(user.password),
            "name": user.name,
            "age": user.age,
            "country": user.country,
            "created_at": datetime.utcnow()
        }
        
        print("✅ User document created")
        
        # Insert user into MongoDB
        result = await db.users.insert_one(user_doc)
        print(f"✅ User inserted with ID: {result.inserted_id}")
        
        # Return user response
        return UserResponse(
            id=str(result.inserted_id),
            email=user.email,
            name=user.name,
            age=user.age,
            country=user.country,
            created_at=user_doc["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in register: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/login")
async def login_user(credentials: UserLogin):
    """Login user and return token"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple token for MVP
    token = f"token_{user['_id']}"
    return {"access_token": token, "token_type": "bearer"}

@app.get("/profile/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
    
    # Validate ObjectId format
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Find user by ID
    user = await db.users.find_one({"_id": object_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        age=user.get("age"),
        country=user.get("country"),
        created_at=user.get("created_at")
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

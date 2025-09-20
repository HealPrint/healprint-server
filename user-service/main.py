from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import bcrypt
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime

from database import connect_to_mongo, close_mongo_connection, get_database
from models import UserCreate, UserResponse, UserLogin, UserInDB

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

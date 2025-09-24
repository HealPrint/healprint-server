from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "healprint")

# Global variables for database connection
client = None
database = None

async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        if not MONGODB_URL:
            print("❌ MONGODB_URL environment variable is not set")
            print("💡 Please set the MONGODB_URL environment variable in your deployment platform")
            print("💡 Example: MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database")
            raise ValueError("MONGODB_URL environment variable is not set")
            
        # Configure connection with production settings
        client = AsyncIOMotorClient(
            MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,        # 10 second timeout
            socketTimeoutMS=20000,         # 20 second timeout
            maxPoolSize=10,                # Maximum number of connections
            retryWrites=True,              # Enable retryable writes
        )
        database = client[DATABASE_NAME]
        
        # Test the connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB successfully")
        print(f"🔗 Connection URL: {MONGODB_URL[:50]}...")  # Truncate URL for security
        print(f"📊 Database: {DATABASE_NAME}")
        return database
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print(f"🔗 Connection URL: {MONGODB_URL[:50] if MONGODB_URL else 'Not set'}...")
        print(f"💡 Make sure MongoDB is running and accessible")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")

def get_database():
    """Get database instance"""
    return database

# Lifespan context manager for database connection
@asynccontextmanager
async def lifespan(app):
    # Startup
    await connect_to_mongo()
    # Initialize cache service
    from cache_service import conversation_cache
    await conversation_cache.connect()
    yield
    # Shutdown
    await conversation_cache.disconnect()
    await close_mongo_connection()

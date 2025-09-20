from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

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
        print(f"🔗 Connection URL: {MONGODB_URL}")
        print(f"📊 Database: {DATABASE_NAME}")
        return database
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print(f"🔗 Connection URL: {MONGODB_URL}")
        print(f"💡 Make sure MongoDB is running and accessible")
        raise e

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return database

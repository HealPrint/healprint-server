#!/usr/bin/env python3
"""
Test script to verify MongoDB connection
"""
import asyncio
import os
from database import connect_to_mongo, close_mongo_connection

async def test_connection():
    """Test MongoDB connection"""
    try:
        print("🔍 Testing MongoDB connection...")
        print(f"📋 MONGODB_URL: {os.getenv('MONGODB_URL', 'Not set')}")
        print(f"📋 DATABASE_NAME: {os.getenv('DATABASE_NAME', 'healprint')}")
        
        db = await connect_to_mongo()
        
        # Test basic operations
        print("🧪 Testing basic operations...")
        
        # Test collection access
        users_collection = db.users
        print(f"✅ Users collection accessible: {users_collection.name}")
        
        # Test insert and find
        test_doc = {"test": "connection", "timestamp": "now"}
        result = await users_collection.insert_one(test_doc)
        print(f"✅ Insert test document: {result.inserted_id}")
        
        # Test find
        found_doc = await users_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Find test document: {found_doc is not None}")
        
        # Clean up test document
        await users_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleaned up test document")
        
        print("🎉 MongoDB connection test successful!")
        
    except Exception as e:
        print(f"❌ MongoDB connection test failed: {e}")
        return False
    finally:
        await close_mongo_connection()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)

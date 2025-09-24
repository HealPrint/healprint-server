from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from contextlib import asynccontextmanager
import logging

from healAgent import HealPrintAIAgent
from config import OPENROUTER_API_KEY, SITE_URL, SITE_NAME
from database import connect_to_mongo, close_mongo_connection, get_database, lifespan
from models import (
    ChatMessage, ChatResponse, Conversation, Message, 
    ConversationHistory, ConversationSummary
)
from conversation_service import ConversationService
from cache_service import conversation_cache

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("chat-service")

masked_key = (OPENROUTER_API_KEY[:6] + "..." + OPENROUTER_API_KEY[-4:]) if OPENROUTER_API_KEY else "Not set"
logger.info(f"Startup config: SITE_URL={SITE_URL} SITE_NAME={SITE_NAME} OPENROUTER_API_KEY={masked_key}")

app = FastAPI(
    title="HealPrint Chat Service", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent
try:
    ai_agent = HealPrintAIAgent()
    if ai_agent is None:
        logger.warning("AI agent is None after initialization")
except Exception as e:
    logger.exception(f"AI Agent initialization failed: {e}")
    ai_agent = None

# Database dependency
async def get_db() -> AsyncIOMotorDatabase:
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
    return db

@app.get("/")
async def root():
    return {"service": "HealPrint Chat Service", "status": "running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(chat_message: ChatMessage, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Process chat message and return AI response"""
    logger.info(f"/chat called for user_id={chat_message.user_id}")
    # Check if AI agent is available
    if ai_agent is None:
        logger.error("AI agent unavailable")
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    
    # Find existing conversation for this user or create new one
    existing_conversation = await db.conversations.find_one({
        "user_id": chat_message.user_id,
        "assessment_stage": {"$ne": "completed"}
    })
    
    if existing_conversation:
        conversation_id = existing_conversation["conversation_id"]
        conversation_obj = Conversation(**existing_conversation)
    else:
        # Create new conversation
        conversation_id = f"conv_{chat_message.user_id}_{int(datetime.utcnow().timestamp())}"
        conversation_obj = Conversation(
            conversation_id=conversation_id,
            user_id=chat_message.user_id,
            title=chat_message.message[:50] + "..." if len(chat_message.message) > 50 else chat_message.message
        )
    
    # Use AI Agent for professional health conversation
    try:
        ai_response = ai_agent.chat_with_user(
            user_message=chat_message.message,
            user_id=chat_message.user_id,
            conversation_id=conversation_id
        )
        if ai_response.get("error"):
            logger.error(f"AI fallback/error: {ai_response['error']}")
        else:
            logger.info("AI response generated successfully")
    except Exception as e:
        logger.exception(f"AI processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")
    
    # Create message objects
    user_message = Message(
        role="user",
        content=chat_message.message,
        message_id=f"msg_{int(datetime.utcnow().timestamp())}_user"
    )
    
    assistant_message = Message(
        role="assistant",
        content=ai_response["response"],
        message_id=f"msg_{int(datetime.utcnow().timestamp())}_assistant"
    )
    
    # Add messages to conversation
    conversation_obj.messages.extend([user_message, assistant_message])
    conversation_obj.updated_at = datetime.utcnow()
    conversation_obj.assessment_stage = ai_response["assessment_stage"]
    conversation_obj.symptoms_collected = ai_response["symptoms_collected"]
    conversation_obj.needs_diagnosis = ai_response["needs_diagnosis"]
    
    # Save to database
    if existing_conversation:
        await db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": conversation_obj.model_dump(by_alias=True, exclude={"id"})}
        )
    else:
        await db.conversations.insert_one(conversation_obj.model_dump(by_alias=True, exclude={"id"}))
    
    return ChatResponse(
        response=ai_response["response"],
        conversation_id=conversation_id,
        message_id=assistant_message.message_id,
        assessment_stage=ai_response["assessment_stage"],
        symptoms_collected=ai_response["symptoms_collected"],
        needs_diagnosis=ai_response["needs_diagnosis"]
    )

@app.get("/conversation/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get conversation history with professional caching"""
    conversation_service = ConversationService(db)
    conversation = await conversation_service.get_conversation_with_cache(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@app.get("/conversations/{user_id}")
async def get_user_conversations(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all conversations for a user with professional caching"""
    conversation_service = ConversationService(db)
    conversations = await conversation_service.get_user_conversations_with_cache(user_id)
    
    return {"user_id": user_id, "conversations": [conv.model_dump() for conv in conversations]}

@app.post("/conversations/new")
async def create_new_conversation(user_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new conversation for a user with professional optimization"""
    conversation_service = ConversationService(db)
    
    # Mark any existing incomplete conversation as completed
    await db.conversations.update_many(
        {"user_id": user_id, "assessment_stage": {"$ne": "completed"}},
        {"$set": {"assessment_stage": "completed"}}
    )
    
    # Create new conversation using optimized service
    conversation_id = await conversation_service.create_conversation_optimized(user_id, "New Chat")
    
    return {"conversation_id": conversation_id, "message": "New conversation created"}

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Delete a conversation with cache invalidation"""
    # Get user_id before deleting for cache invalidation
    conversation = await db.conversations.find_one(
        {"conversation_id": conversation_id}, 
        {"user_id": 1}
    )
    
    result = await db.conversations.delete_one({"conversation_id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Invalidate caches
    await conversation_cache.invalidate_conversation(conversation_id)
    if conversation:
        await conversation_cache.invalidate_user_conversations(conversation["user_id"])
    
    return {"message": "Conversation deleted successfully"}

@app.post("/analyze/{conversation_id}")
async def analyze_conversation(conversation_id: str):
    """Generate comprehensive diagnostic analysis for a conversation"""
    if ai_agent is None:
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    
    try:
        analysis = ai_agent.generate_diagnostic_analysis(conversation_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/conversation/{conversation_id}/summary")
async def get_conversation_summary(conversation_id: str):
    """Get summary of a conversation"""
    if ai_agent is None:
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable")
    
    try:
        summary = ai_agent.get_conversation_summary(conversation_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chat-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

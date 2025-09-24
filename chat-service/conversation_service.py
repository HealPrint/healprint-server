"""
Professional Conversation Service for HealPrint Chat
Handles conversation loading, caching, and streaming with optimized performance
"""

import asyncio
from typing import Optional, Dict, List, Any, AsyncGenerator
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from models import Conversation, Message, ConversationHistory, ConversationSummary
from cache_service import conversation_cache

logger = logging.getLogger(__name__)

class ConversationService:
    """Professional conversation management service"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.conversations_collection = db.conversations
    
    async def get_conversation_with_cache(self, conversation_id: str) -> Optional[ConversationHistory]:
        """
        Get conversation with intelligent caching strategy
        Returns conversation data optimized for frontend consumption
        """
        try:
            # First, try to get from cache
            cached_conversation = await conversation_cache.get_conversation(conversation_id)
            if cached_conversation:
                logger.info(f"Conversation {conversation_id} loaded from cache")
                return self._convert_cached_to_conversation_history(cached_conversation)
            
            # If not in cache, fetch from database
            logger.info(f"Fetching conversation {conversation_id} from database")
            conversation_doc = await self.conversations_collection.find_one({
                "conversation_id": conversation_id
            })
            
            if not conversation_doc:
                logger.warning(f"Conversation {conversation_id} not found")
                return None
            
            # Convert to frontend format
            conversation_history = self._convert_db_to_conversation_history(conversation_doc)
            
            # Cache the conversation for future requests
            await conversation_cache.cache_conversation(
                conversation_id, 
                self._convert_conversation_to_cache_format(conversation_doc)
            )
            
            logger.info(f"Conversation {conversation_id} loaded from database and cached")
            return conversation_history
            
        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id}: {e}")
            return None
    
    async def get_user_conversations_with_cache(self, user_id: str) -> List[ConversationSummary]:
        """
        Get user conversations with intelligent caching
        Returns optimized conversation summaries for sidebar
        """
        try:
            # First, try to get from cache
            cached_conversations = await conversation_cache.get_user_conversations(user_id)
            if cached_conversations:
                logger.info(f"User {user_id} conversations loaded from cache")
                return [ConversationSummary(**conv) for conv in cached_conversations]
            
            # If not in cache, fetch from database
            logger.info(f"Fetching conversations for user {user_id} from database")
            cursor = self.conversations_collection.find(
                {"user_id": user_id}
            ).sort("updated_at", -1).limit(50)  # Limit to 50 most recent
            
            conversations = []
            async for doc in cursor:
                conversation_summary = ConversationSummary(
                    conversation_id=doc["conversation_id"],
                    title=doc.get("title", "New Conversation"),
                    last_message=doc.get("last_message", ""),
                    message_count=len(doc.get("messages", [])),
                    created_at=doc.get("created_at", datetime.now()),
                    updated_at=doc.get("updated_at", datetime.now()),
                )
                conversations.append(conversation_summary)
            
            # Cache the conversations
            await conversation_cache.cache_user_conversations(
                user_id,
                [conv.model_dump() for conv in conversations]
            )
            
            logger.info(f"User {user_id} conversations loaded from database and cached")
            return conversations
            
        except Exception as e:
            logger.error(f"Error loading conversations for user {user_id}: {e}")
            return []
    
    async def create_conversation_optimized(self, user_id: str, title: str = "New Conversation") -> str:
        """
        Create new conversation with optimized performance
        """
        try:
            conversation_id = f"conv_{user_id}_{int(datetime.now().timestamp())}"
            
            conversation_doc = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "title": title,
                "messages": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "assessment_stage": "initial",
                "symptoms_collected": {},
                "needs_diagnosis": False,
                "last_message": ""
            }
            
            await self.conversations_collection.insert_one(conversation_doc)
            
            # Invalidate user conversations cache
            await conversation_cache.invalidate_user_conversations(user_id)
            
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating conversation for user {user_id}: {e}")
            raise
    
    async def update_conversation_optimized(
        self, 
        conversation_id: str, 
        message: Message,
        assessment_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update conversation with new message and invalidate cache
        """
        try:
            update_data = {
                "messages": {"$push": message.model_dump()},
                "updated_at": datetime.now(),
                "last_message": message.content[:100]  # First 100 chars
            }
            
            if assessment_data:
                update_data.update(assessment_data)
            
            result = await self.conversations_collection.update_one(
                {"conversation_id": conversation_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Invalidate conversation cache
                await conversation_cache.invalidate_conversation(conversation_id)
                
                # Get user_id to invalidate user conversations cache
                conversation = await self.conversations_collection.find_one(
                    {"conversation_id": conversation_id},
                    {"user_id": 1}
                )
                if conversation:
                    await conversation_cache.invalidate_user_conversations(conversation["user_id"])
                
                logger.info(f"Updated conversation {conversation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating conversation {conversation_id}: {e}")
            return False
    
    def _convert_db_to_conversation_history(self, doc: Dict[str, Any]) -> ConversationHistory:
        """Convert database document to ConversationHistory format"""
        messages = []
        for msg in doc.get("messages", []):
            messages.append(Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            ))
        
        return ConversationHistory(
            conversation_id=doc["conversation_id"],
            user_id=doc["user_id"],
            title=doc.get("title", "New Conversation"),
            messages=messages,
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            assessment_stage=doc.get("assessment_stage", "initial"),
            symptoms_collected=doc.get("symptoms_collected", {}),
            needs_diagnosis=doc.get("needs_diagnosis", False)
        )
    
    def _convert_cached_to_conversation_history(self, cached_data: Dict[str, Any]) -> ConversationHistory:
        """Convert cached data to ConversationHistory format"""
        messages = []
        for msg in cached_data.get("messages", []):
            messages.append(Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"]
            ))
        
        return ConversationHistory(
            conversation_id=cached_data["conversation_id"],
            user_id=cached_data["user_id"],
            title=cached_data.get("title", "New Conversation"),
            messages=messages,
            created_at=datetime.fromisoformat(cached_data["created_at"]) if isinstance(cached_data["created_at"], str) else cached_data["created_at"],
            updated_at=datetime.fromisoformat(cached_data["updated_at"]) if isinstance(cached_data["updated_at"], str) else cached_data["updated_at"],
            assessment_stage=cached_data.get("assessment_stage", "initial"),
            symptoms_collected=cached_data.get("symptoms_collected", {}),
            needs_diagnosis=cached_data.get("needs_diagnosis", False)
        )
    
    def _convert_conversation_to_cache_format(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database document to cache-friendly format"""
        return {
            "conversation_id": doc["conversation_id"],
            "user_id": doc["user_id"],
            "title": doc.get("title", "New Conversation"),
            "messages": doc.get("messages", []),
            "created_at": doc["created_at"].isoformat() if isinstance(doc["created_at"], datetime) else doc["created_at"],
            "updated_at": doc["updated_at"].isoformat() if isinstance(doc["updated_at"], datetime) else doc["updated_at"],
            "assessment_stage": doc.get("assessment_stage", "initial"),
            "symptoms_collected": doc.get("symptoms_collected", {}),
            "needs_diagnosis": doc.get("needs_diagnosis", False)
        }

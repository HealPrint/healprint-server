"""
Professional Redis Caching Service for HealPrint Chat
Handles conversation caching, message streaming, and state management
"""

import json
import asyncio
from typing import Optional, Dict, List, Any
import redis.asyncio as redis
from datetime import datetime, timedelta
import logging
from config import REDIS_URL

logger = logging.getLogger(__name__)

class ConversationCache:
    """Professional conversation caching service using Redis"""
    
    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = 3600 * 24  # 24 hours TTL
        
    async def connect(self):
        """Initialize Redis connection"""
        try:
            if not self.redis_url:
                logger.info("REDIS_URL not set - cache disabled")
                self.redis_client = None
                return
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_conversation_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation"""
        return f"conversation:{conversation_id}"
    
    def _get_user_conversations_key(self, user_id: str) -> str:
        """Generate Redis key for user conversations list"""
        return f"user_conversations:{user_id}"
    
    async def cache_conversation(self, conversation_id: str, conversation_data: Dict[str, Any]) -> bool:
        """Cache conversation data with TTL"""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_conversation_key(conversation_id)
            await self.redis_client.setex(
                key, 
                self.cache_ttl, 
                json.dumps(conversation_data, default=str)
            )
            logger.info(f"Cached conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache conversation {conversation_id}: {e}")
            return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve conversation from cache"""
        if not self.redis_client:
            return None
        
        try:
            key = self._get_conversation_key(conversation_id)
            cached_data = await self.redis_client.get(key)
            if cached_data:
                logger.info(f"Retrieved conversation {conversation_id} from cache")
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve conversation {conversation_id}: {e}")
            return None
    
    async def cache_user_conversations(self, user_id: str, conversations: List[Dict[str, Any]]) -> bool:
        """Cache user's conversation list"""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_user_conversations_key(user_id)
            await self.redis_client.setex(
                key,
                self.cache_ttl,
                json.dumps(conversations, default=str)
            )
            logger.info(f"Cached {len(conversations)} conversations for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache user conversations for {user_id}: {e}")
            return False
    
    async def get_user_conversations(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve user's conversation list from cache"""
        if not self.redis_client:
            return None
        
        try:
            key = self._get_user_conversations_key(user_id)
            cached_data = await self.redis_client.get(key)
            if cached_data:
                logger.info(f"Retrieved conversations for user {user_id} from cache")
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve user conversations for {user_id}: {e}")
            return None
    
    async def invalidate_conversation(self, conversation_id: str) -> bool:
        """Remove conversation from cache"""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_conversation_key(conversation_id)
            await self.redis_client.delete(key)
            logger.info(f"Invalidated conversation {conversation_id} from cache")
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate conversation {conversation_id}: {e}")
            return False
    
    async def invalidate_user_conversations(self, user_id: str) -> bool:
        """Remove user's conversation list from cache"""
        if not self.redis_client:
            return False
        
        try:
            key = self._get_user_conversations_key(user_id)
            await self.redis_client.delete(key)
            logger.info(f"Invalidated conversations for user {user_id} from cache")
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate user conversations for {user_id}: {e}")
            return False

# Global cache instance
conversation_cache = ConversationCache()

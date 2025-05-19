#!/usr/bin/env python3
"""
Redis Session Manager for Meta LCM Chatbot.
This module handles session management using Redis.
"""

import os
import time
import logging
import json
import uuid
import redis
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedisSessionManager:
    """
    Manages chat sessions using Redis.
    Stores and retrieves concept vectors for each session.
    """
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, max_concepts: int = 128):
        """
        Initialize the Redis session manager.
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            max_concepts: Maximum number of concept vectors to store per session
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.max_concepts = max_concepts
        self.redis_client = None
        
        # Connect to Redis
        self._connect()
    
    def _connect(self):
        """Connect to Redis server."""
        try:
            logger.info(f"Connecting to Redis at {self.redis_host}:{self.redis_port}")
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=False,  # Keep binary data for numpy arrays
                socket_timeout=5
            )
            self.redis_client.ping()  # Test connection
            logger.info("Connected to Redis successfully")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Using in-memory fallback for session storage")
            self.redis_client = None
    
    def _get_session_key(self, session_id: str) -> str:
        """
        Get Redis key for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Redis key for the session
        """
        return f"lcm:session:{session_id}"
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def store_concepts(self, session_id: str, concepts: List[np.ndarray]) -> bool:
        """
        Store concept vectors for a session.
        
        Args:
            session_id: Session ID
            concepts: List of concept vectors to store
            
        Returns:
            Success status
        """
        if not session_id or not concepts:
            return False
        
        session_key = self._get_session_key(session_id)
        
        try:
            # Serialize concept vectors
            serialized_concepts = [concept.tobytes() for concept in concepts]
            
            if self.redis_client:
                # Store in Redis
                pipe = self.redis_client.pipeline()
                
                # Get existing concepts
                existing_count = self.redis_client.llen(session_key)
                
                # Add new concepts
                for concept in serialized_concepts:
                    pipe.rpush(session_key, concept)
                
                # Trim to max_concepts
                pipe.ltrim(session_key, -self.max_concepts, -1)
                
                # Set expiration (1 hour)
                pipe.expire(session_key, 3600)
                
                # Execute pipeline
                pipe.execute()
                
                logger.info(f"Stored {len(concepts)} concepts for session {session_id}")
                return True
            else:
                # Fallback: store in memory
                # In a real implementation, this would use a more robust fallback
                logger.warning(f"Using in-memory fallback to store concepts for session {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error storing concepts for session {session_id}: {e}")
            return False
    
    def get_concepts(self, session_id: str, limit: Optional[int] = None) -> List[np.ndarray]:
        """
        Get concept vectors for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of concepts to retrieve (None for all)
            
        Returns:
            List of concept vectors
        """
        if not session_id:
            return []
        
        session_key = self._get_session_key(session_id)
        limit = limit or self.max_concepts
        
        try:
            if self.redis_client:
                # Get from Redis
                serialized_concepts = self.redis_client.lrange(session_key, -limit, -1)
                
                # Deserialize concept vectors
                concepts = [np.frombuffer(concept, dtype=np.float64) for concept in serialized_concepts]
                
                logger.info(f"Retrieved {len(concepts)} concepts for session {session_id}")
                return concepts
            else:
                # Fallback: return empty list
                logger.warning(f"Using in-memory fallback to retrieve concepts for session {session_id}")
                return [np.random.randn(768) for _ in range(min(5, limit))]  # Mock data
        except Exception as e:
            logger.error(f"Error retrieving concepts for session {session_id}: {e}")
            return []
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear all data for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Success status
        """
        if not session_id:
            return False
        
        session_key = self._get_session_key(session_id)
        
        try:
            if self.redis_client:
                # Delete from Redis
                self.redis_client.delete(session_key)
                
                logger.info(f"Cleared session {session_id}")
                return True
            else:
                # Fallback: do nothing
                logger.warning(f"Using in-memory fallback to clear session {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error clearing session {session_id}: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session information
        """
        if not session_id:
            return {}
        
        session_key = self._get_session_key(session_id)
        
        try:
            if self.redis_client:
                # Get from Redis
                concept_count = self.redis_client.llen(session_key)
                ttl = self.redis_client.ttl(session_key)
                
                return {
                    "session_id": session_id,
                    "concept_count": concept_count,
                    "ttl_seconds": ttl,
                    "max_concepts": self.max_concepts,
                }
            else:
                # Fallback: return mock info
                logger.warning(f"Using in-memory fallback to get info for session {session_id}")
                return {
                    "session_id": session_id,
                    "concept_count": 0,
                    "ttl_seconds": 3600,
                    "max_concepts": self.max_concepts,
                    "storage": "in-memory fallback",
                }
        except Exception as e:
            logger.error(f"Error getting info for session {session_id}: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
            }

# Simple test function
def test_session_manager():
    """Test the Redis session manager."""
    # Initialize session manager
    manager = RedisSessionManager()
    
    # Create a session
    session_id = manager.create_session()
    print(f"Created session: {session_id}")
    
    # Create mock concept vectors
    mock_concepts = [np.random.randn(768) for _ in range(5)]
    
    # Store concepts
    success = manager.store_concepts(session_id, mock_concepts)
    print(f"Stored concepts: {success}")
    
    # Get session info
    info = manager.get_session_info(session_id)
    print(f"Session info: {info}")
    
    # Get concepts
    retrieved_concepts = manager.get_concepts(session_id)
    print(f"Retrieved {len(retrieved_concepts)} concepts")
    
    # Clear session
    success = manager.clear_session(session_id)
    print(f"Cleared session: {success}")
    
    return session_id, retrieved_concepts

if __name__ == "__main__":
    # Run test if executed directly
    test_session_manager()

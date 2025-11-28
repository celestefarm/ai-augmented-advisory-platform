# agents/utils/cache.py

"""
Unified Caching Layer for AI Agents

Provides centralized caching for:
- System prompts (Claude, Gemini, Ollama)
- User context
- Agent responses
- Model outputs

Backend: Redis
Fallback: In-memory dict (if Redis unavailable)
"""

import redis
import hashlib
import json
import logging
from typing import Optional, Dict, Any
from datetime import timedelta
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Centralized cache manager for all AI agents
    
    Features:
    - Redis backend with in-memory fallback
    - TTL-based expiration
    - Automatic serialization/deserialization
    - Cache key namespacing
    - Async support
    """
    
    # Cache TTL configurations (in seconds)
    TTL_SYSTEM_PROMPT = 3600      # 1 hour
    TTL_USER_CONTEXT = 300        # 5 minutes
    TTL_AGENT_RESPONSE = 900      # 15 minutes
    TTL_MODEL_OUTPUT = 1800       # 30 minutes
    
    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        use_fallback: bool = True
    ):
        """
        Initialize cache manager
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            redis_password: Redis password (optional)
            use_fallback: Use in-memory fallback if Redis unavailable
        """
        self.use_fallback = use_fallback
        self.fallback_cache = {}  # In-memory fallback
        
        try:
            # Initialize Redis connection
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,  # Auto-decode bytes to strings
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info(f"✅ Redis cache connected: {redis_host}:{redis_port}")
            
        except Exception as e:
            self.redis_available = False
            if use_fallback:
                logger.warning(f"⚠️ Redis unavailable, using in-memory fallback: {str(e)}")
            else:
                logger.error(f"❌ Redis connection failed: {str(e)}")
                raise
    
    def _generate_key(self, namespace: str, identifier: str) -> str:
        """
        Generate cache key with namespace
        
        Args:
            namespace: Cache namespace (e.g., 'system_prompt', 'user_context')
            identifier: Unique identifier (will be hashed)
            
        Returns:
            Cache key string
        """
        # Hash identifier for consistent key length
        hash_id = hashlib.md5(identifier.encode()).hexdigest()
        return f"ai_agents:{namespace}:{hash_id}"
    
    def get(self, namespace: str, identifier: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            
        Returns:
            Cached value or None
        """
        key = self._generate_key(namespace, identifier)
        
        if self.redis_available:
            try:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"✅ Cache HIT: {namespace}")
                else:
                    logger.debug(f"❌ Cache MISS: {namespace}")
                return value
            except Exception as e:
                logger.error(f"Redis GET error: {str(e)}")
                if self.use_fallback:
                    return self.fallback_cache.get(key)
                return None
        else:
            return self.fallback_cache.get(key)
    
    def set(
        self,
        namespace: str,
        identifier: str,
        value: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            value: Value to cache
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        key = self._generate_key(namespace, identifier)
        
        if self.redis_available:
            try:
                if ttl:
                    self.redis_client.setex(key, ttl, value)
                else:
                    self.redis_client.set(key, value)
                logger.debug(f"✅ Cache SET: {namespace} (TTL: {ttl}s)")
                return True
            except Exception as e:
                logger.error(f"Redis SET error: {str(e)}")
                if self.use_fallback:
                    self.fallback_cache[key] = value
                    return True
                return False
        else:
            self.fallback_cache[key] = value
            return True
    
    def get_json(self, namespace: str, identifier: str) -> Optional[Dict]:
        """Get JSON value from cache"""
        value = self.get(namespace, identifier)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from cache: {namespace}")
                return None
        return None
    
    def set_json(
        self,
        namespace: str,
        identifier: str,
        value: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache"""
        try:
            json_str = json.dumps(value)
            return self.set(namespace, identifier, json_str, ttl)
        except Exception as e:
            logger.error(f"Failed to encode JSON for cache: {str(e)}")
            return False
    
    def delete(self, namespace: str, identifier: str) -> bool:
        """Delete value from cache"""
        key = self._generate_key(namespace, identifier)
        
        if self.redis_available:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis DELETE error: {str(e)}")
                return False
        else:
            self.fallback_cache.pop(key, None)
            return True
    
    def clear_namespace(self, namespace: str) -> int:
        """
        Clear all keys in a namespace
        
        Args:
            namespace: Cache namespace to clear
            
        Returns:
            Number of keys deleted
        """
        if self.redis_available:
            try:
                pattern = f"ai_agents:{namespace}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"Cleared {deleted} keys from namespace: {namespace}")
                    return deleted
                return 0
            except Exception as e:
                logger.error(f"Redis CLEAR error: {str(e)}")
                return 0
        else:
            # Clear from fallback
            pattern = f"ai_agents:{namespace}:"
            keys_to_delete = [k for k in self.fallback_cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                del self.fallback_cache[key]
            return len(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.redis_available:
            try:
                info = self.redis_client.info('stats')
                return {
                    'backend': 'redis',
                    'total_keys': self.redis_client.dbsize(),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                    'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
                }
            except Exception as e:
                logger.error(f"Redis STATS error: {str(e)}")
                return {'backend': 'redis', 'error': str(e)}
        else:
            return {
                'backend': 'memory',
                'total_keys': len(self.fallback_cache)
            }
    
    # ========================================================================
    # HELPER METHODS FOR SPECIFIC CACHE TYPES
    # ========================================================================
    
    def get_system_prompt(self, agent_name: str, prompt_hash: str) -> Optional[str]:
        """Get cached system prompt for agent"""
        identifier = f"{agent_name}:{prompt_hash}"
        return self.get('system_prompt', identifier)
    
    def set_system_prompt(self, agent_name: str, prompt_hash: str, prompt: str) -> bool:
        """Cache system prompt for agent"""
        identifier = f"{agent_name}:{prompt_hash}"
        return self.set('system_prompt', identifier, prompt, self.TTL_SYSTEM_PROMPT)
    
    def get_user_context(self, user_id: str) -> Optional[str]:
        """Get cached user context"""
        return self.get('user_context', user_id)
    
    def set_user_context(self, user_id: str, context: str) -> bool:
        """Cache user context"""
        return self.set('user_context', user_id, context, self.TTL_USER_CONTEXT)
    
    def get_agent_response(self, question_hash: str, agent_name: str) -> Optional[Dict]:
        """Get cached agent response"""
        identifier = f"{agent_name}:{question_hash}"
        return self.get_json('agent_response', identifier)
    
    def set_agent_response(
        self,
        question_hash: str,
        agent_name: str,
        response: Dict
    ) -> bool:
        """Cache agent response"""
        identifier = f"{agent_name}:{question_hash}"
        return self.set_json('agent_response', identifier, response, self.TTL_AGENT_RESPONSE)
    
    def get_model_output(self, model_name: str, input_hash: str) -> Optional[str]:
        """Get cached model output"""
        identifier = f"{model_name}:{input_hash}"
        return self.get('model_output', identifier)
    
    def set_model_output(
        self,
        model_name: str,
        input_hash: str,
        output: str
    ) -> bool:
        """Cache model output"""
        identifier = f"{model_name}:{input_hash}"
        return self.set('model_output', identifier, output, self.TTL_MODEL_OUTPUT)


# ============================================================================
# SINGLETON PATTERN - Single cache instance for entire application
# ============================================================================

_cache_instance: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get singleton cache manager instance
    
    Returns:
        CacheManager instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        from decouple import config
        
        _cache_instance = CacheManager(
            redis_host=config('REDIS_HOST', default='localhost'),
            redis_port=config('REDIS_PORT', default=6379, cast=int),
            redis_db=config('REDIS_DB', default=0, cast=int),
            redis_password=config('REDIS_PASSWORD', default=None),
            use_fallback=True
        )
    
    return _cache_instance


# ============================================================================
# DECORATOR FOR AUTOMATIC CACHING
# ============================================================================

def cached_model_call(namespace: str, ttl: int):
    """
    Decorator to automatically cache model calls
    
    Usage:
        @cached_model_call('claude_output', 1800)
        async def call_claude(prompt):
            # ... actual API call
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key from function args
            cache_key_parts = [func.__name__]
            cache_key_parts.extend([str(arg) for arg in args])
            cache_key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = cache.get(namespace, cache_key)
            if cached_result:
                logger.info(f"✅ Using cached result for {func.__name__}")
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(namespace, cache_key, result, ttl)
            logger.info(f"💾 Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator


# Example usage
if __name__ == '__main__':
    # Initialize cache
    cache = get_cache_manager()
    
    # Test system prompt caching
    cache.set_system_prompt('strategy_analyst', 'v1', 'You are a strategy analyst...')
    prompt = cache.get_system_prompt('strategy_analyst', 'v1')
    print(f"System Prompt: {prompt[:50]}...")
    
    # Test user context caching
    cache.set_user_context('user123', 'CEO at Series A startup')
    context = cache.get_user_context('user123')
    print(f"User Context: {context}")
    
    # Test agent response caching
    cache.set_agent_response(
        'q_hash_123',
        'strategy_analyst',
        {'decision_reframe': 'test', 'confidence': 'high'}
    )
    response = cache.get_agent_response('q_hash_123', 'strategy_analyst')
    print(f"Agent Response: {response}")
    
    # Get stats
    stats = cache.get_stats()
    print(f"\nCache Stats: {stats}")
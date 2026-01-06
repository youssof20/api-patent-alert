"""
Redis caching service
"""
import json
from typing import Optional, Any
from datetime import timedelta
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Try to import redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Caching and rate limiting will be disabled. Install with: pip install redis")


class CacheService:
    """Redis cache service for patent data and rate limiting"""
    
    def __init__(self):
        if not REDIS_AVAILABLE:
            self.redis_client = None
            self.default_ttl = settings.redis_cache_ttl
            logger.warning("Redis not available. Running without cache.")
            return
        
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.default_ttl = settings.redis_cache_ttl
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Running without cache.")
            self.redis_client = None
            self.default_ttl = settings.redis_cache_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.redis_client:
            return False
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.exists(key))
        except Exception:
            return False
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter (for rate limiting)"""
        if not self.redis_client:
            return 0
        try:
            return self.redis_client.incrby(key, amount)
        except Exception:
            return 0
    
    def set_expiry(self, key: str, seconds: int) -> bool:
        """Set expiry on existing key"""
        if not self.redis_client:
            return False
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception:
            return False
    
    def get_rate_limit_count(self, api_key: str, window: str = "minute") -> int:
        """Get current rate limit count for API key"""
        if not self.redis_client:
            return 0
        key = f"rate_limit:{api_key}:{window}"
        try:
            count = self.redis_client.get(key)
            return int(count) if count else 0
        except (ValueError, Exception):
            return 0
    
    def increment_rate_limit(self, api_key: str, window: str = "minute", ttl: int = 60) -> int:
        """Increment rate limit counter"""
        if not self.redis_client:
            return 0
        key = f"rate_limit:{api_key}:{window}"
        try:
            count = self.redis_client.incr(key)
            if count == 1:  # First request, set expiry
                self.redis_client.expire(key, ttl)
            return count
        except Exception:
            return 0
    
    def reset_rate_limit(self, api_key: str, window: str = "minute") -> bool:
        """Reset rate limit counter"""
        key = f"rate_limit:{api_key}:{window}"
        return self.delete(key)


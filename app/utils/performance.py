"""
Performance optimization utilities
"""
from functools import wraps
import time
import logging
from typing import Callable, Any
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)
cache_service = CacheService()


def cache_result(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = cache_service.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_service.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        
        if elapsed > 1.0:
            logger.warning(f"{func.__name__} took {elapsed:.3f}s")
        else:
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        
        return result
    return wrapper


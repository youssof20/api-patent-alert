"""
API dependencies for authentication and rate limiting
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import APIKey
from app.services.cache_service import CacheService
from app.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
cache_service = CacheService()


async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Dependency to authenticate API key
    
    Args:
        x_api_key: API key from header
        db: Database session
        
    Returns:
        APIKey model instance
        
    Raises:
        HTTPException if authentication fails
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header. Get one from POST /api/v1/auth/keys",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Query database for API key
    api_key = db.query(APIKey).filter(
        APIKey.key == x_api_key,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}... (truncated)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key. Get a valid key from POST /api/v1/auth/keys",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Check if key is expired
    if api_key.expires_at and api_key.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    return api_key


def check_rate_limit(api_key: APIKey) -> bool:
    """
    Check if API key has exceeded rate limits
    
    Args:
        api_key: APIKey model instance
        
    Returns:
        True if within limits, False otherwise
    """
    # Check per-minute limit
    minute_count = cache_service.get_rate_limit_count(api_key.key, "minute")
    if minute_count >= api_key.rate_limit_per_minute:
        return False
    
    # Check per-day limit
    day_count = cache_service.get_rate_limit_count(api_key.key, "day")
    if day_count >= api_key.rate_limit_per_day:
        return False
    
    return True


def increment_rate_limit(api_key: APIKey):
    """Increment rate limit counters"""
    cache_service.increment_rate_limit(api_key.key, "minute", ttl=60)
    cache_service.increment_rate_limit(api_key.key, "day", ttl=86400)


async def verify_api_key_and_rate_limit(
    api_key: APIKey = Depends(get_api_key)
) -> APIKey:
    """
    Combined dependency for authentication and rate limiting
    
    Args:
        api_key: Authenticated API key
        
    Returns:
        APIKey model instance
        
    Raises:
        HTTPException if rate limit exceeded
    """
    if not check_rate_limit(api_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Increment counters
    increment_rate_limit(api_key)
    
    return api_key


"""
Monitoring and metrics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.monitoring import get_metrics
from app.api.deps import verify_api_key_and_rate_limit
from app.models.user import APIKey

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])


@router.get("/metrics")
async def get_api_metrics(
    api_key: APIKey = Depends(verify_api_key_and_rate_limit)
):
    """
    Get API performance metrics.
    
    Requires admin API key or special permission.
    """
    # In production, check if API key has admin permissions
    # For now, allow any authenticated user
    metrics = get_metrics()
    return metrics


@router.get("/health/detailed", include_in_schema=False)
async def detailed_health_check():
    """
    Detailed health check with system status.
    
    No authentication required.
    """
    from app.config import settings
    from app.services.cache_service import CacheService
    from app.database import SessionLocal
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "services": {}
    }
    
    # Check Redis
    try:
        cache = CacheService()
        if cache.redis_client:
            cache.redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "disabled"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
    
    # Check Database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
    
    # Check USPTO API (basic connectivity)
    health_status["services"]["uspto_api"] = "configured" if settings.uspto_api_key else "not_configured"
    
    # Overall status
    if any("unhealthy" in str(v) for v in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return health_status


"""
Health check endpoint
"""
from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health Check",
    description="Check API health and status. No authentication required.",
    tags=["Health"]
)
async def health_check():
    """Health check endpoint. No authentication required."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API is operational. Visit /docs for API documentation."
    }


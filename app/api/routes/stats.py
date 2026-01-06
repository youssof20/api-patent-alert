"""
Usage statistics endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict
from app.database import get_db
from app.models.user import APIKey
from app.models.usage import APIUsage
from app.api.deps import verify_api_key_and_rate_limit

router = APIRouter(prefix="/api/v1/stats", tags=["Statistics"])


@router.get(
    "",
    summary="Get Usage Statistics",
    description="Get usage statistics for your API key. Requires authentication.",
    response_description="Usage statistics including query counts, costs, and analytics"
)
async def get_usage_stats(
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """Get usage statistics for current API key. Returns queries, costs, response times, and rate limits."""
    
    # Get stats for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Total queries
    total_queries = db.query(func.count(APIUsage.id)).filter(
        APIUsage.api_key_id == api_key.id,
        APIUsage.created_at >= thirty_days_ago
    ).scalar() or 0
    
    # Total cost
    total_cost = db.query(func.sum(APIUsage.cost)).filter(
        APIUsage.api_key_id == api_key.id,
        APIUsage.created_at >= thirty_days_ago
    ).scalar() or 0.0
    
    # Average response time
    avg_response_time = db.query(func.avg(APIUsage.response_time_ms)).filter(
        APIUsage.api_key_id == api_key.id,
        APIUsage.created_at >= thirty_days_ago,
        APIUsage.response_time_ms.isnot(None)
    ).scalar() or 0.0
    
    # Queries by endpoint
    endpoint_stats = db.query(
        APIUsage.endpoint,
        func.count(APIUsage.id).label("count")
    ).filter(
        APIUsage.api_key_id == api_key.id,
        APIUsage.created_at >= thirty_days_ago
    ).group_by(APIUsage.endpoint).all()
    
    # Daily usage (last 7 days)
    daily_usage = []
    for i in range(7):
        date = datetime.utcnow().date() - timedelta(days=i)
        count = db.query(func.count(APIUsage.id)).filter(
            func.date(APIUsage.created_at) == date,
            APIUsage.api_key_id == api_key.id
        ).scalar() or 0
        daily_usage.append({
            "date": date.isoformat(),
            "count": count
        })
    
    return {
        "period": "last_30_days",
        "total_queries": total_queries,
        "total_cost": round(float(total_cost), 2),
        "average_response_time_ms": round(float(avg_response_time), 2),
        "endpoints": [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in endpoint_stats
        ],
        "daily_usage": list(reversed(daily_usage)),
        "rate_limits": {
            "per_minute": api_key.rate_limit_per_minute,
            "per_day": api_key.rate_limit_per_day
        }
    }


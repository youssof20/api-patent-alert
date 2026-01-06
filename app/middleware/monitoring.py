"""
Monitoring and metrics middleware
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable
from app.config import settings

logger = logging.getLogger(__name__)

# Simple in-memory metrics (in production, use Prometheus, Datadog, etc.)
metrics = {
    "requests_total": 0,
    "requests_by_status": {},
    "requests_by_endpoint": {},
    "response_times": [],
    "errors": []
}


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for request monitoring and metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Track request
        metrics["requests_total"] += 1
        endpoint = f"{request.method} {request.url.path}"
        metrics["requests_by_endpoint"][endpoint] = metrics["requests_by_endpoint"].get(endpoint, 0) + 1
        
        try:
            response = await call_next(request)
            
            # Track response status
            status_code = response.status_code
            metrics["requests_by_status"][status_code] = metrics["requests_by_status"].get(status_code, 0) + 1
            
            # Track response time
            response_time = time.time() - start_time
            metrics["response_times"].append(response_time)
            
            # Keep only last 1000 response times
            if len(metrics["response_times"]) > 1000:
                metrics["response_times"] = metrics["response_times"][-1000:]
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{response_time:.3f}s"
            
            # Log slow requests
            if response_time > 1.0:
                logger.warning(f"Slow request: {endpoint} took {response_time:.3f}s")
            
            return response
            
        except Exception as e:
            # Track errors
            metrics["errors"].append({
                "endpoint": endpoint,
                "error": str(e),
                "timestamp": time.time()
            })
            
            # Keep only last 100 errors
            if len(metrics["errors"]) > 100:
                metrics["errors"] = metrics["errors"][-100:]
            
            logger.error(f"Request error: {endpoint} - {e}")
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )


def get_metrics() -> dict:
    """Get current metrics"""
    response_times = metrics["response_times"]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    return {
        "requests_total": metrics["requests_total"],
        "requests_by_status": metrics["requests_by_status"],
        "requests_by_endpoint": dict(list(metrics["requests_by_endpoint"].items())[:10]),  # Top 10
        "average_response_time_ms": round(avg_response_time * 1000, 2),
        "p95_response_time_ms": round(sorted(response_times)[int(len(response_times) * 0.95)] * 1000, 2) if response_times else 0,
        "error_count": len(metrics["errors"]),
        "recent_errors": metrics["errors"][-10:] if metrics["errors"] else []
    }


"""
Main FastAPI application
"""
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from app.config import settings
from app.database import init_db
from app.api.routes import health, expirations, auth, webhooks, stats, monitoring
from app.api.routes import stripe as stripe_routes
from app.middleware.monitoring import MonitoringMiddleware
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Define API Key security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## B2B White-Label API for Patent Expiration Alerts

Automated patent expiration monitoring for IP/Legal SaaS platforms. Integrate in <1 day.

### Quick Start

1. **Create API Key**: Use `POST /api/v1/auth/keys` below (no auth required)
2. **Authorize**: Click 🔒 button (top right) and enter your API key
3. **Test**: Try `/health` first, then `/api/v1/expirations`

### Key Features

- Real-time patent expiration alerts
- AI-powered filtering and summarization
- Industry-specific queries (biotech, electronics, software, medical, automotive, energy, materials)
- White-label support (remove API branding)
- Webhook integration for real-time notifications

### Pricing Tiers

- **Free Trial**: 14 days, 100 queries/day
- **Starter**: $500/month, 5,000 queries/month
- **Professional**: $2,000/month, 25,000 queries/month
- **Enterprise**: Custom pricing, unlimited queries

**Contact**: youssofsallam25@gmail.com
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "API Support",
        "email": "youssofsallam25@gmail.com",
    },
    license_info={
        "name": "Proprietary",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api-patent-alert.onrender.com",
            "description": "Production server (Render)"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitoring middleware
if settings.enable_metrics:
    app.add_middleware(MonitoringMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(expirations.router)
app.include_router(auth.router)
app.include_router(webhooks.router)
app.include_router(stats.router)
app.include_router(monitoring.router)
app.include_router(stripe_routes.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logging.info(f"{settings.app_name} v{settings.app_version} started")
    
    # Start background scheduler for webhooks
    try:
        from app.services.scheduler import SchedulerService
        scheduler = SchedulerService()
        # Run scheduler in background
        asyncio.create_task(scheduler.run_scheduler())
        app.state.scheduler = scheduler
        logging.info("Background scheduler started")
    except Exception as e:
        logging.warning(f"Failed to start scheduler: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Stop scheduler
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.stop()
    logging.info(f"{settings.app_name} shutting down")


def custom_openapi():
    """Custom OpenAPI schema with security schemes"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter your API key. Get one by calling POST /api/v1/auth/keys\n\n⚠️ Note: Swagger UI shows 'Authorized' when you enter any value, but validation happens when you make a request. Invalid keys will return 401 Unauthorized."
        }
    }
    
    # Add security to all protected endpoints
    for path, path_item in openapi_schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                # Skip health and root endpoints
                if path in ["/health", "/"]:
                    continue
                # Skip auth key creation endpoint (no auth required)
                if path == "/api/v1/auth/keys" and method == "post":
                    continue
                # Skip billing webhook (uses Stripe signature, not API key)
                if path == "/api/v1/billing/webhook" and method == "post":
                    continue
                # Skip detailed health check (public endpoint)
                if path == "/api/v1/monitoring/health/detailed":
                    continue
                # Add security requirement
                if "security" not in operation:
                    operation["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
async def root():
    """
    Root endpoint - API information
    
    No authentication required.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "B2B White-Label API for Patent Expiration Alerts",
        "docs": "/docs",
        "health": "/health"
    }


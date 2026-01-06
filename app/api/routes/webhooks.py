"""
Webhook management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from app.database import get_db
from app.models.user import APIKey, WebhookConfig
from app.api.deps import verify_api_key_and_rate_limit
from app.utils.helpers import generate_api_key
from datetime import datetime

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


class WebhookCreate(BaseModel):
    """Request model for creating webhook"""
    url: HttpUrl
    secret: Optional[str] = None
    events: Optional[List[str]] = ["patent.expired"]


class WebhookResponse(BaseModel):
    """Response model for webhook"""
    id: str
    url: str
    is_active: bool
    events: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post(
    "", 
    response_model=WebhookResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create Webhook",
    description="Register a webhook endpoint for real-time patent expiration alerts. Requires authentication.",
)
async def create_webhook(
    webhook_data: WebhookCreate,
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """Register a webhook endpoint. Webhook receives POST requests when patents expire. Optional secret for HMAC verification."""
    # Check if webhook already exists for this API key and URL
    existing = db.query(WebhookConfig).filter(
        WebhookConfig.api_key_id == api_key.id,
        WebhookConfig.url == str(webhook_data.url)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook already registered for this URL"
        )
    
    # Create webhook config
    webhook = WebhookConfig(
        api_key_id=api_key.id,
        url=str(webhook_data.url),
        secret=webhook_data.secret,
        events=",".join(webhook_data.events) if webhook_data.events else None,
        is_active=True
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.get(
    "", 
    response_model=List[WebhookResponse],
    summary="List Webhooks",
    description="Get all registered webhook endpoints for your API key. Requires authentication."
)
async def list_webhooks(
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """List all webhooks for current API key. Returns active webhook configurations."""
    webhooks = db.query(WebhookConfig).filter(
        WebhookConfig.api_key_id == api_key.id
    ).all()
    
    return webhooks


@router.delete(
    "/{webhook_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete Webhook",
    description="Remove a webhook endpoint registration. Requires authentication."
)
async def delete_webhook(
    webhook_id: str,
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """Delete a webhook. Permanently removes the endpoint. You can only delete webhooks associated with your API key."""
    webhook = db.query(WebhookConfig).filter(
        WebhookConfig.id == webhook_id,
        WebhookConfig.api_key_id == api_key.id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    return {"message": "Webhook deleted successfully"}


"""
API key management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import APIKey
from app.api.deps import verify_api_key_and_rate_limit
from app.utils.helpers import generate_api_key
from app.api.deps import get_api_key as verify_api_key

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class APIKeyCreate(BaseModel):
    """Request model for creating API key"""
    partner_name: str
    partner_email: EmailStr
    rate_limit_per_minute: Optional[int] = 60
    rate_limit_per_day: Optional[int] = 10000
    branding_enabled: Optional[bool] = True
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    """Response model for API key"""
    id: str
    key: str
    partner_name: str
    partner_email: str
    is_active: bool
    rate_limit_per_minute: int
    rate_limit_per_day: int
    branding_enabled: bool
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.post(
    "/keys", 
    response_model=APIKeyResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create API Key",
    description="""
    Create a new API key (self-service signup).
    
    **No authentication required**. Save your API key - it won't be shown again.
    
    Free trial: 14 days, 100 queries/day.
    """,
    response_description="API key object with your new key"
)
async def create_api_key(
    key_data: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new API key for a partner
    
    **Self-Service Signup** - No authentication required.
    
    After creating your API key:
    1. Copy the `key` value from the response
    2. Click the 🔒 "Authorize" button in Swagger UI
    3. Paste your API key and click "Authorize"
    4. Start testing endpoints!
    
    **Note**: In production, this endpoint may require admin approval.
    """
    # Check if email already has an active key
    existing = db.query(APIKey).filter(
        APIKey.partner_email == key_data.partner_email,
        APIKey.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active API key already exists for this email"
        )
    
    # Generate new API key
    new_key = generate_api_key()
    
    # Calculate expiration date if provided
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Create API key record
    api_key = APIKey(
        key=new_key,
        partner_name=key_data.partner_name,
        partner_email=key_data.partner_email,
        rate_limit_per_minute=key_data.rate_limit_per_minute,
        rate_limit_per_day=key_data.rate_limit_per_day,
        branding_enabled=key_data.branding_enabled,
        expires_at=expires_at
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # Send welcome email
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        email_service.send_welcome_email(
            partner_email=key_data.partner_email,
            partner_name=key_data.partner_name,
            api_key=new_key
        )
    except Exception as e:
        logger.warning(f"Failed to send welcome email: {e}")
    
    return api_key


@router.get("/keys/me", response_model=APIKeyResponse)
async def get_current_api_key(
    api_key: APIKey = Depends(verify_api_key_and_rate_limit)
):
    """Get current API key information"""
    return api_key


@router.post("/keys/{key_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    key_id: str,
    db: Session = Depends(get_db)
):
    """
    Revoke an API key
    
    Note: In production, this should be protected by admin authentication
    """
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key revoked successfully"}


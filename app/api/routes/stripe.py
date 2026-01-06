"""
Stripe payment processing endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import stripe
import logging
from app.database import get_db
from app.models.user import APIKey
from app.models.usage import APIUsage
from app.api.deps import verify_api_key_and_rate_limit
from app.config import settings

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])

# Initialize Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature")
):
    """
    Handle Stripe webhook events.
    
    No authentication required (verified via Stripe signature).
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook secret not configured"
        )
    
    payload = await request.body()
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle event
    event_type = event['type']
    data = event['data']['object']
    
    logger.info(f"Stripe webhook received: {event_type}")
    
    if event_type == 'customer.subscription.created':
        # New subscription created
        logger.info(f"Subscription created: {data.get('id')}")
        # Update API key subscription status in database
        # Implementation depends on your subscription model
        
    elif event_type == 'customer.subscription.updated':
        # Subscription updated
        logger.info(f"Subscription updated: {data.get('id')}")
        
    elif event_type == 'customer.subscription.deleted':
        # Subscription cancelled
        logger.info(f"Subscription deleted: {data.get('id')}")
        # Deactivate API key or reduce rate limits
        
    elif event_type == 'invoice.payment_succeeded':
        # Payment succeeded
        logger.info(f"Payment succeeded: {data.get('id')}")
        
    elif event_type == 'invoice.payment_failed':
        # Payment failed
        logger.warning(f"Payment failed: {data.get('id')}")
        # Send notification, potentially suspend API key
        
    return {"status": "success"}


@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,  # starter, professional, enterprise
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """
    Create Stripe checkout session for subscription.
    
    Requires authentication.
    """
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe not configured"
        )
    
    # Plan pricing
    plan_prices = {
        "starter": 50000,  # $500 in cents
        "professional": 200000,  # $2000 in cents
        "enterprise": 500000  # $5000 in cents
    }
    
    if plan not in plan_prices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Choose from: {', '.join(plan_prices.keys())}"
        )
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=api_key.partner_email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Patent Alert API - {plan.capitalize()} Plan',
                        'description': f'Monthly subscription for {plan} tier'
                    },
                    'unit_amount': plan_prices[plan],
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{request.base_url}api/v1/billing/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{request.base_url}api/v1/billing/cancel',
            metadata={
                'api_key_id': api_key.id,
                'partner_email': api_key.partner_email
            }
        )
        
        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.get("/success")
async def checkout_success(session_id: str):
    """Handle successful checkout"""
    return {"message": "Payment successful", "session_id": session_id}


@router.get("/cancel")
async def checkout_cancel():
    """Handle cancelled checkout"""
    return {"message": "Payment cancelled"}


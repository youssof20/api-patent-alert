"""
Webhook delivery service
"""
import httpx
import json
import hmac
import hashlib
from typing import Dict, Optional
from datetime import datetime
from app.config import settings
import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for delivering webhooks to partners"""
    
    def __init__(self):
        self.timeout = settings.webhook_timeout
        self.retry_attempts = settings.webhook_retry_attempts
        self.retry_delay = settings.webhook_retry_delay
    
    def generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def deliver_webhook(
        self,
        url: str,
        event_type: str,
        data: Dict,
        secret: Optional[str] = None
    ) -> bool:
        """
        Deliver webhook to partner endpoint
        
        Args:
            url: Webhook URL
            event_type: Type of event (e.g., 'patent.expired')
            data: Event data
            secret: Optional secret for signature generation
            
        Returns:
            True if delivery successful, False otherwise
        """
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        payload_json = json.dumps(payload)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Patent-Alert-API/1.0"
        }
        
        # Add signature if secret provided
        if secret:
            signature = self.generate_signature(payload_json, secret)
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        
        # Retry logic with exponential backoff
        for attempt in range(1, self.retry_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        content=payload_json,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201, 202]:
                        logger.info(f"Webhook delivered successfully to {url} (attempt {attempt})")
                        return True
                    else:
                        logger.warning(
                            f"Webhook delivery failed to {url}: "
                            f"HTTP {response.status_code} (attempt {attempt})"
                        )
                        
            except httpx.TimeoutException:
                logger.warning(f"Webhook timeout for {url} (attempt {attempt})")
            except Exception as e:
                logger.error(f"Webhook delivery error to {url}: {e} (attempt {attempt})")
            
            # Exponential backoff before retry
            if attempt < self.retry_attempts:
                delay = self.retry_delay * (2 ** (attempt - 1))
                import asyncio
                await asyncio.sleep(delay)
        
        logger.error(f"Webhook delivery failed after {self.retry_attempts} attempts to {url}")
        return False
    
    async def notify_patent_expiration(
        self,
        webhook_url: str,
        patent: Dict,
        secret: Optional[str] = None
    ) -> bool:
        """Notify partner of patent expiration"""
        return await self.deliver_webhook(
            webhook_url,
            "patent.expired",
            patent,
            secret
        )


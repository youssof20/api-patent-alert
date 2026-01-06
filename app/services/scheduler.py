"""
Background scheduler for webhook triggering and periodic tasks
"""
import asyncio
from datetime import datetime, timedelta
from typing import List
import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import WebhookConfig
from app.models.patent import PatentExpiration
from app.services.uspto_client import USPTOClient
from app.services.webhook_service import WebhookService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduled background tasks"""
    
    def __init__(self):
        self.uspto_client = USPTOClient()
        self.webhook_service = WebhookService()
        self.ai_service = AIService()
        self.running = False
    
    async def check_expiring_patents_and_trigger_webhooks(self):
        """Check for patents expiring today/tomorrow and trigger webhooks"""
        db = SessionLocal()
        try:
            # Get patents expiring in next 2 days
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            day_after = today + timedelta(days=2)
            
            # Query for expiring patents
            expiring_patents = db.query(PatentExpiration).filter(
                PatentExpiration.expiration_date >= datetime.combine(today, datetime.min.time()),
                PatentExpiration.expiration_date < datetime.combine(day_after, datetime.max.time())
            ).all()
            
            if not expiring_patents:
                logger.info("No patents expiring in next 2 days")
                return
            
            # Get all active webhooks
            webhooks = db.query(WebhookConfig).filter(
                WebhookConfig.is_active == True
            ).all()
            
            if not webhooks:
                logger.info("No active webhooks registered")
                return
            
            # Trigger webhooks for each expiring patent
            triggered_count = 0
            for patent in expiring_patents:
                patent_data = {
                    "patent_id": patent.id,
                    "title": patent.title,
                    "abstract": patent.abstract,
                    "expiration_date": patent.expiration_date.isoformat(),
                    "grant_date": patent.grant_date.isoformat() if patent.grant_date else None,
                    "inventor": patent.inventor,
                    "assignee": patent.assignee,
                    "technology_area": patent.technology_area,
                    "ai_summary": patent.ai_summary,
                    "relevance_score": patent.relevance_score
                }
                
                # Send to all registered webhooks
                for webhook in webhooks:
                    # Check if webhook is for patent.expired event
                    events = webhook.events.split(",") if webhook.events else []
                    if "patent.expired" in events or not events:
                        success = await self.webhook_service.notify_patent_expiration(
                            webhook.url,
                            patent_data,
                            webhook.secret
                        )
                        if success:
                            triggered_count += 1
                            logger.info(f"Webhook triggered for patent {patent.id} to {webhook.url}")
            
            logger.info(f"Triggered {triggered_count} webhooks for {len(expiring_patents)} expiring patents")
            
        except Exception as e:
            logger.error(f"Error in webhook scheduler: {e}")
        finally:
            db.close()
    
    async def refresh_patent_cache(self):
        """Periodically refresh patent expiration cache"""
        db = SessionLocal()
        try:
            # Get patents expiring in next 90 days
            today = datetime.utcnow().date()
            future_date = today + timedelta(days=90)
            
            # Query USPTO for fresh data
            patents = await self.uspto_client.get_expiring_patents(
                start_date=datetime.combine(today, datetime.min.time()),
                end_date=datetime.combine(future_date, datetime.max.time()),
                limit=1000
            )
            
            # Process with AI
            processed = self.ai_service.process_patents(patents)
            
            # Update database cache
            for patent in processed:
                existing = db.query(PatentExpiration).filter(
                    PatentExpiration.id == patent["id"]
                ).first()
                
                if existing:
                    # Update existing
                    existing.title = patent.get("title")
                    existing.abstract = patent.get("abstract")
                    existing.expiration_date = patent.get("expiration_date")
                    existing.grant_date = patent.get("grant_date")
                    existing.inventor = patent.get("inventor")
                    existing.assignee = patent.get("assignee")
                    existing.technology_area = patent.get("technology_area")
                    existing.ai_summary = patent.get("ai_summary")
                    existing.relevance_score = patent.get("relevance_score")
                else:
                    # Create new
                    new_patent = PatentExpiration(
                        id=patent["id"],
                        title=patent.get("title", ""),
                        abstract=patent.get("abstract"),
                        grant_date=patent.get("grant_date"),
                        expiration_date=patent.get("expiration_date"),
                        inventor=patent.get("inventor"),
                        assignee=patent.get("assignee"),
                        technology_area=patent.get("technology_area"),
                        ai_summary=patent.get("ai_summary"),
                        relevance_score=patent.get("relevance_score")
                    )
                    db.add(new_patent)
            
            db.commit()
            logger.info(f"Refreshed patent cache with {len(processed)} patents")
            
        except Exception as e:
            logger.error(f"Error refreshing patent cache: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def run_scheduler(self):
        """Main scheduler loop"""
        self.running = True
        logger.info("Scheduler started")
        
        while self.running:
            try:
                # Check expiring patents every hour
                await self.check_expiring_patents_and_trigger_webhooks()
                
                # Refresh cache daily (at midnight UTC)
                now = datetime.utcnow()
                if now.hour == 0 and now.minute < 5:
                    await self.refresh_patent_cache()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")


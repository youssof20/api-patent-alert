"""
User and API key models
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime


class APIKey(Base):
    """API Key model for partner authentication"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False, index=True)
    partner_name = Column(String, nullable=False)
    partner_email = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_day = Column(Integer, default=10000)
    branding_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    usage_records = relationship("APIUsage", back_populates="api_key", cascade="all, delete-orphan")
    webhook_configs = relationship("WebhookConfig", back_populates="api_key", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<APIKey(partner_name='{self.partner_name}', is_active={self.is_active})>"


class WebhookConfig(Base):
    """Webhook configuration for partners"""
    __tablename__ = "webhook_configs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=True)  # For webhook signature verification
    is_active = Column(Boolean, default=True)
    events = Column(Text, nullable=True)  # JSON array of event types
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    api_key = relationship("APIKey", back_populates="webhook_configs")
    
    def __repr__(self):
        return f"<WebhookConfig(url='{self.url}', is_active={self.is_active})>"


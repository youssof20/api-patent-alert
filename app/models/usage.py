"""
API usage tracking models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class APIUsage(Base):
    """API usage tracking for billing and analytics"""
    __tablename__ = "api_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    query_params = Column(Text, nullable=True)  # JSON string
    response_status = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=True)
    query_count = Column(Integer, default=1)  # Number of patents returned
    cost = Column(Float, nullable=True)  # Calculated cost for billing
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    api_key = relationship("APIKey", back_populates="usage_records")
    
    def __repr__(self):
        return f"<APIUsage(endpoint='{self.endpoint}', status={self.response_status})>"


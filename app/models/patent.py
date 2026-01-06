"""
Patent data models
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Index
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class PatentExpiration(Base):
    """Cached patent expiration data"""
    __tablename__ = "patent_expirations"
    
    id = Column(String, primary_key=True)  # Patent number
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    grant_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False, index=True)
    inventor = Column(String, nullable=True)
    assignee = Column(String, nullable=True)
    patent_type = Column(String, nullable=True)  # utility, design, plant, etc.
    industry_keywords = Column(Text, nullable=True)  # JSON array of keywords
    ai_summary = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    technology_area = Column(String, nullable=True)
    cached_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_expiration_date', 'expiration_date'),
        Index('idx_technology_area', 'technology_area'),
    )
    
    def __repr__(self):
        return f"<PatentExpiration(id='{self.id}', expiration_date='{self.expiration_date}')>"


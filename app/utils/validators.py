"""
Input validation utilities
"""
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, validator


class ExpirationQueryParams(BaseModel):
    """Validation model for expiration query parameters"""
    industry: Optional[str] = None
    date_range: Optional[str] = "next_30_days"
    limit: int = 50
    offset: int = 0
    branding: bool = True
    
    @validator("limit")
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        return v
    
    @validator("offset")
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v
    
    @validator("date_range")
    def validate_date_range(cls, v):
        valid_ranges = ["next_7_days", "next_30_days", "next_90_days", "next_365_days", "custom"]
        if v not in valid_ranges:
            raise ValueError(f"Date range must be one of: {', '.join(valid_ranges)}")
        return v
    
    def get_date_range_tuple(self) -> tuple[datetime, datetime]:
        """Convert date_range string to datetime tuple"""
        today = datetime.now().date()
        
        if self.date_range == "next_7_days":
            end_date = today + timedelta(days=7)
        elif self.date_range == "next_30_days":
            end_date = today + timedelta(days=30)
        elif self.date_range == "next_90_days":
            end_date = today + timedelta(days=90)
        elif self.date_range == "next_365_days":
            end_date = today + timedelta(days=365)
        else:
            end_date = today + timedelta(days=30)  # Default
        
        start_date = today
        return (datetime.combine(start_date, datetime.min.time()), 
                datetime.combine(end_date, datetime.max.time()))


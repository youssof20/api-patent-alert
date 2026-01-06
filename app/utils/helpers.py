"""
Helper utility functions
"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import json


def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"pat_{secrets.token_urlsafe(32)}"


def calculate_patent_expiration(grant_date: datetime) -> datetime:
    """Calculate patent expiration date (20 years from grant date)"""
    return grant_date + timedelta(days=365 * 20)


def hash_webhook_secret(secret: str) -> str:
    """Hash webhook secret for storage"""
    return hashlib.sha256(secret.encode()).hexdigest()


def format_patent_response(patent: dict, branding: bool = True) -> dict:
    """Format patent data for API response"""
    response = {
        "patent_id": patent.get("id"),
        "title": patent.get("title"),
        "abstract": patent.get("abstract"),
        "expiration_date": patent.get("expiration_date").isoformat() if patent.get("expiration_date") else None,
        "grant_date": patent.get("grant_date").isoformat() if patent.get("grant_date") else None,
        "inventor": patent.get("inventor"),
        "assignee": patent.get("assignee"),
        "technology_area": patent.get("technology_area"),
        "summary": patent.get("ai_summary"),
        "relevance_score": patent.get("relevance_score"),
    }
    
    if branding:
        response["powered_by"] = "Patent Alert API"
    
    return response


def parse_industry_keywords(industry: Optional[str]) -> list[str]:
    """Parse industry string into keyword list"""
    if not industry:
        return []
    
    # Common industry mappings
    industry_map = {
        "biotech": ["biotechnology", "pharmaceutical", "drug", "medicine", "therapeutic"],
        "electronics": ["electronic", "circuit", "semiconductor", "chip", "processor"],
        "software": ["software", "algorithm", "computer", "system", "method"],
        "medical": ["medical", "device", "surgical", "diagnostic", "treatment"],
        "automotive": ["vehicle", "automotive", "engine", "transmission", "brake"],
    }
    
    industry_lower = industry.lower()
    if industry_lower in industry_map:
        return industry_map[industry_lower]
    
    # Return single keyword if not in map
    return [industry_lower]


def calculate_billing_cost(query_count: int, cost_per_query: float = 0.50) -> float:
    """Calculate billing cost based on query count"""
    return round(query_count * cost_per_query, 2)


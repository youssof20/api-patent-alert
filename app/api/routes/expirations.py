"""
Patent expiration endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models.user import APIKey
from app.models.patent import PatentExpiration
from app.models.usage import APIUsage
from app.api.deps import verify_api_key_and_rate_limit
from app.services.uspto_client import USPTOClient
from app.services.ai_service import AIService
from app.utils.validators import ExpirationQueryParams
from app.utils.helpers import format_patent_response, parse_industry_keywords, calculate_billing_cost
from app.utils.validators import ExpirationQueryParams
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/expirations", tags=["Expirations"])

uspto_client = USPTOClient()
ai_service = AIService()


@router.get(
    "",
    summary="Get Expiring Patents",
    description="""
    Query patents expiring in the specified date range with AI-powered filtering.
    
    **Requires API Key** - Click 🔒 Authorize button (top right).
    
    **Industries**: biotech, electronics, software, medical, automotive, energy, materials
    
    Returns patent data with AI summaries and relevance scores.
    """,
    response_description="List of expiring patents with AI summaries and metadata"
)
async def get_expiring_patents(
    industry: Optional[str] = Query(
        None, 
        description="Industry filter. Options: biotech, electronics, software, medical, automotive, energy, materials",
        example="biotech"
    ),
    date_range: str = Query(
        "next_30_days", 
        description="Date range for expirations",
        example="next_30_days"
    ),
    limit: int = Query(
        50, 
        ge=1, 
        le=1000, 
        description="Maximum number of results (1-1000)",
        example=50
    ),
    offset: int = Query(
        0, 
        ge=0, 
        description="Offset for pagination",
        example=0
    ),
    branding: bool = Query(
        True, 
        description="Include API provider branding in response. Set to false for white-label.",
        example=True
    ),
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """
    Get patents expiring in the specified date range.
    
    **Authentication Required**: Include API key in `X-API-Key` header.
    
    **Parameters**:
    - `industry`: Filter by industry (biotech, electronics, software, etc.)
    - `date_range`: next_7_days, next_30_days, next_90_days, next_365_days
    - `limit`: Max results (1-1000, default: 50)
    - `offset`: Pagination offset (default: 0)
    - `branding`: Include API branding (default: true, false for white-label)
    
    **Returns**: Patent objects with AI summaries, relevance scores, and metadata.
    """
    start_time = time.time()
    
    try:
        # Validate query parameters
        query_params = ExpirationQueryParams(
            industry=industry,
            date_range=date_range,
            limit=limit,
            offset=offset,
            branding=branding if api_key.branding_enabled else False
        )
        
        # Get date range
        start_date, end_date = query_params.get_date_range_tuple()
        
        # Parse industry keywords
        industry_keywords = parse_industry_keywords(query_params.industry)
        
        # Query USPTO API
        patents = await uspto_client.get_expiring_patents(
            start_date=start_date,
            end_date=end_date,
            industry_keywords=industry_keywords if industry_keywords else None,
            limit=query_params.limit,
            offset=query_params.offset
        )
        
        # Process with AI
        processed_patents = ai_service.process_patents(patents, industry_keywords)
        
        # Format response
        response_data = [
            format_patent_response(patent, query_params.branding)
            for patent in processed_patents
        ]
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Track usage for billing
        usage = APIUsage(
            api_key_id=api_key.id,
            endpoint="/api/v1/expirations",
            method="GET",
            query_params=str(query_params.dict()),
            response_status=200,
            response_time_ms=response_time_ms,
            query_count=len(response_data),
            cost=calculate_billing_cost(len(response_data))
        )
        db.add(usage)
        db.commit()
        
        return {
            "data": response_data,
            "count": len(response_data),
            "limit": query_params.limit,
            "offset": query_params.offset,
            "total_estimated": len(response_data)  # In production, get actual total from USPTO
        }
        
    except Exception as e:
        logger.error(f"Error fetching expiring patents: {e}")
        
        # Track failed usage
        usage = APIUsage(
            api_key_id=api_key.id,
            endpoint="/api/v1/expirations",
            method="GET",
            response_status=500,
            response_time_ms=(time.time() - start_time) * 1000
        )
        db.add(usage)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching patent data"
        )


@router.get(
    "/{patent_id}",
    summary="Get Patent by ID",
    description="""
    Get detailed information about a specific patent by ID.
    
    **Requires API Key** - Click 🔒 Authorize button (top right).
    
    Patent ID format: US12345678
    """,
    response_description="Detailed patent information with AI summary"
)
async def get_patent_by_id(
    patent_id: str,
    api_key: APIKey = Depends(verify_api_key_and_rate_limit),
    db: Session = Depends(get_db)
):
    """
    Get single patent by ID.
    
    **Authentication Required**: Include API key in `X-API-Key` header.
    
    Returns detailed patent information with AI summary.
    """
    start_time = time.time()
    
    try:
        patent = await uspto_client.get_patent_by_id(patent_id)
        
        if not patent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patent {patent_id} not found"
            )
        
        # Process with AI
        processed = ai_service.process_patents([patent])
        if processed:
            patent = processed[0]
        
        # Format response
        response_data = format_patent_response(
            patent,
            api_key.branding_enabled
        )
        
        # Track usage
        usage = APIUsage(
            api_key_id=api_key.id,
            endpoint=f"/api/v1/expirations/{patent_id}",
            method="GET",
            response_status=200,
            response_time_ms=(time.time() - start_time) * 1000,
            query_count=1,
            cost=calculate_billing_cost(1)
        )
        db.add(usage)
        db.commit()
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patent {patent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching patent data"
        )


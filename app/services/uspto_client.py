"""
USPTO API client for patent data
"""
import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.config import settings
from app.services.cache_service import CacheService
from app.utils.helpers import calculate_patent_expiration
import logging

logger = logging.getLogger(__name__)


class USPTOClient:
    """Client for querying USPTO PatentsView API"""
    
    def __init__(self):
        self.api_key = settings.uspto_api_key
        self.base_url = settings.uspto_patentsview_url
        self.cache = CacheService()
        self.timeout = 30.0
    
    def _get_cache_key(self, query_params: dict) -> str:
        """Generate cache key from query parameters"""
        key_str = json.dumps(query_params, sort_keys=True)
        return f"uspto_query:{hash(key_str)}"
    
    def _build_query(self, start_date: datetime, end_date: datetime,
                     industry_keywords: Optional[List[str]] = None) -> dict:
        """Build PatentsView API query"""
        # Calculate grant dates (20 years before expiration)
        grant_start = start_date - timedelta(days=365 * 20)
        grant_end = end_date - timedelta(days=365 * 20)
        
        # Base query for patents granted in date range
        query = {
            "_gte": {
                "patent_date": grant_start.strftime("%Y-%m-%d")
            },
            "_lte": {
                "patent_date": grant_end.strftime("%Y-%m-%d")
            }
        }
        
        # Add industry keyword filter if provided
        if industry_keywords:
            keyword_query = {
                "_or": [
                    {"_text_any": {"patent_abstract": keyword}}
                    for keyword in industry_keywords
                ]
            }
            query = {"_and": [query, keyword_query]}
        
        return query
    
    async def get_expiring_patents(
        self,
        start_date: datetime,
        end_date: datetime,
        industry_keywords: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get patents expiring in the specified date range
        
        Args:
            start_date: Start of expiration date range
            end_date: End of expiration date range
            industry_keywords: Optional list of keywords to filter by
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of patent dictionaries
        """
        # Check cache first
        cache_key = self._get_cache_key({
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "keywords": industry_keywords or [],
            "limit": limit,
            "offset": offset
        })
        
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for query: {cache_key}")
            return cached_result
        
        # Build query
        query = self._build_query(start_date, end_date, industry_keywords)
        
        # PatentsView API request
        request_data = {
            "q": query,
            "f": [
                "patent_number",
                "patent_title",
                "patent_abstract",
                "patent_date",
                "inventor_last_name",
                "assignee_organization"
            ],
            "o": {
                "per_page": limit,
                "page": (offset // limit) + 1
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["X-API-Key"] = self.api_key
                
                response = await client.post(
                    self.base_url,
                    json=request_data,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                patents = data.get("patents", [])
                
                # Process and enrich patent data
                processed_patents = self._process_patents(patents, start_date, end_date)
                
                # Cache results
                self.cache.set(cache_key, processed_patents, ttl=3600)  # 1 hour cache
                
                return processed_patents
                
        except httpx.HTTPError as e:
            logger.error(f"USPTO API error: {e}")
            # Fallback to bulk data API if available
            return await self._fallback_bulk_data_query(start_date, end_date, industry_keywords, limit, offset)
        except Exception as e:
            logger.error(f"Unexpected error querying USPTO: {e}")
            return []
    
    def _process_patents(self, patents: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """Process raw patent data and calculate expiration dates"""
        processed = []
        
        for patent in patents:
            try:
                patent_number = patent.get("patent_number", "")
                patent_date_str = patent.get("patent_date", "")
                
                if not patent_date_str:
                    continue
                
                # Parse grant date
                grant_date = datetime.strptime(patent_date_str, "%Y-%m-%d")
                
                # Calculate expiration date (20 years from grant)
                expiration_date = calculate_patent_expiration(grant_date)
                
                # Filter by expiration date range
                if not (start_date <= expiration_date <= end_date):
                    continue
                
                # Extract inventor and assignee
                inventors = patent.get("inventors", [])
                inventor_name = ", ".join([
                    f"{inv.get('inventor_last_name', '')}, {inv.get('inventor_first_name', '')}"
                    for inv in inventors[:3]  # Limit to first 3
                ]) if inventors else None
                
                assignees = patent.get("assignees", [])
                assignee_name = assignees[0].get("assignee_organization", "") if assignees else None
                
                processed_patent = {
                    "id": patent_number,
                    "title": patent.get("patent_title", "Untitled Patent"),
                    "abstract": patent.get("patent_abstract", ""),
                    "grant_date": grant_date,
                    "expiration_date": expiration_date,
                    "inventor": inventor_name,
                    "assignee": assignee_name,
                    "patent_type": "utility",  # Default, can be enhanced
                    "technology_area": None,  # Will be filled by AI service
                    "ai_summary": None,  # Will be filled by AI service
                    "relevance_score": None  # Will be filled by AI service
                }
                
                processed.append(processed_patent)
                
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing patent {patent.get('patent_number', 'unknown')}: {e}")
                continue
        
        return processed
    
    async def _fallback_bulk_data_query(
        self,
        start_date: datetime,
        end_date: datetime,
        industry_keywords: Optional[List[str]],
        limit: int,
        offset: int
    ) -> List[Dict]:
        """Fallback to bulk data API if PatentsView fails"""
        # This is a simplified fallback - in production, you'd implement
        # full bulk data parsing
        logger.warning("Using fallback bulk data query (limited functionality)")
        return []
    
    async def get_patent_by_id(self, patent_id: str) -> Optional[Dict]:
        """Get single patent by ID"""
        cache_key = f"patent:{patent_id}"
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            query = {"patent_number": patent_id}
            request_data = {
                "q": query,
                "f": [
                    "patent_number",
                    "patent_title",
                    "patent_abstract",
                    "patent_date",
                    "inventor_last_name",
                    "assignee_organization"
                ]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["X-API-Key"] = self.api_key
                
                response = await client.post(
                    self.base_url,
                    json=request_data,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                patents = data.get("patents", [])
                
                if patents:
                    patent = patents[0]
                    processed = self._process_patents([patent], datetime.min, datetime.max)
                    if processed:
                        result = processed[0]
                        self.cache.set(cache_key, result, ttl=86400)  # 24 hour cache
                        return result
                
                return None
                
        except Exception as e:
            logger.error(f"Error fetching patent {patent_id}: {e}")
            return None


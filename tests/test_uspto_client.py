"""
Tests for USPTO client
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from app.services.uspto_client import USPTOClient


@pytest.fixture
def uspto_client():
    """Create USPTO client instance"""
    return USPTOClient()


@pytest.mark.asyncio
async def test_get_expiring_patents(uspto_client):
    """Test getting expiring patents"""
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=30)
    
    # Mock the HTTP client
    with patch("app.services.uspto_client.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "patents": [{
                "patent_number": "US12345678",
                "patent_title": "Test Patent",
                "patent_abstract": "Test abstract",
                "patent_date": "2004-01-01",
                "inventors": [{"inventor_last_name": "Doe", "inventor_first_name": "John"}],
                "assignees": [{"assignee_organization": "Test Corp"}]
            }]
        }
        mock_response.raise_for_status = AsyncMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance
        
        patents = await uspto_client.get_expiring_patents(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
        
        # Should return processed patents
        assert isinstance(patents, list)


def test_calculate_patent_expiration():
    """Test patent expiration calculation"""
    from app.utils.helpers import calculate_patent_expiration
    
    grant_date = datetime(2004, 1, 1)
    expiration = calculate_patent_expiration(grant_date)
    
    # Should be 20 years later
    expected = datetime(2024, 1, 1)
    assert expiration.year == expected.year
    assert expiration.month == expected.month
    assert expiration.day == expected.day


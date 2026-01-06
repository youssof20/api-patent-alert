"""
Tests for expiration endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app.models.user import APIKey
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_api_key(db):
    """Create test API key"""
    api_key = APIKey(
        key="test_api_key_123",
        partner_name="Test Partner",
        partner_email="test@example.com",
        is_active=True,
        rate_limit_per_minute=100,
        rate_limit_per_day=10000
    )
    db.add(api_key)
    db.commit()
    return api_key


@pytest.fixture
def mock_patent_data():
    """Mock patent data"""
    return [{
        "id": "US12345678",
        "title": "Test Patent",
        "abstract": "This is a test patent abstract",
        "grant_date": datetime.now() - timedelta(days=365 * 19),
        "expiration_date": datetime.now() + timedelta(days=365),
        "inventor": "John Doe",
        "assignee": "Test Corp",
        "patent_type": "utility",
        "technology_area": None,
        "ai_summary": None,
        "relevance_score": None
    }]


@patch("app.api.routes.expirations.uspto_client.get_expiring_patents")
def test_get_expirations(mock_get_patents, client, test_api_key, mock_patent_data):
    """Test getting expiring patents"""
    mock_get_patents.return_value = mock_patent_data
    
    response = client.get(
        "/api/v1/expirations",
        headers={"X-API-Key": test_api_key.key},
        params={"limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data


@patch("app.api.routes.expirations.uspto_client.get_patent_by_id")
def test_get_patent_by_id(mock_get_patent, client, test_api_key, mock_patent_data):
    """Test getting single patent by ID"""
    mock_get_patent.return_value = mock_patent_data[0]
    
    response = client.get(
        "/api/v1/expirations/US12345678",
        headers={"X-API-Key": test_api_key.key}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["patent_id"] == "US12345678"


def test_expirations_query_params(client, test_api_key):
    """Test query parameters validation"""
    response = client.get(
        "/api/v1/expirations",
        headers={"X-API-Key": test_api_key.key},
        params={"limit": 2000}  # Exceeds max limit
    )
    
    # Should return validation error
    assert response.status_code in [400, 422]


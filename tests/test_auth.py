"""
Tests for authentication
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, Base, engine
from app.models.user import APIKey
from sqlalchemy.orm import sessionmaker

# Create test database
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
        is_active=True
    )
    db.add(api_key)
    db.commit()
    return api_key


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_key_required(client):
    """Test that API key is required"""
    response = client.get("/api/v1/expirations")
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]


def test_invalid_api_key(client):
    """Test invalid API key"""
    response = client.get(
        "/api/v1/expirations",
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_valid_api_key(client, test_api_key):
    """Test valid API key"""
    # Mock USPTO client to avoid actual API calls
    # This is a simplified test - in production, mock the USPTO client
    response = client.get(
        "/api/v1/expirations",
        headers={"X-API-Key": test_api_key.key}
    )
    # Should not be 401 (authentication passed)
    # May be 500 or other error if USPTO client not mocked
    assert response.status_code != 401


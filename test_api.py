"""
Quick test script to verify API is working and create an API key
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint (no auth required)"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"[OK] Health check: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\nTesting / endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"[OK] Root endpoint: {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"[FAIL] Root endpoint failed: {e}")
        return False

def create_api_key():
    """Create an API key"""
    print("\nCreating API key...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/keys",
            json={
                "partner_name": "Test Partner",
                "partner_email": "test@example.com",
                "rate_limit_per_minute": 60,
                "rate_limit_per_day": 10000,
                "branding_enabled": True
            },
            timeout=5
        )
        if response.status_code == 201:
            data = response.json()
            api_key = data["key"]
            print(f"[OK] API Key created successfully!")
            print(f"  API Key: {api_key}")
            print(f"\n[WARNING] SAVE THIS KEY - You'll need it for testing!")
            return api_key
        else:
            print(f"[FAIL] Failed to create API key: {response.status_code}")
            print(f"  Response: {response.text}")
            # Maybe key already exists, try to get it
            if "already exists" in response.text:
                print("\n  Trying to get existing key info...")
                # We can't get the key back, but we can tell user to check admin dashboard
                print("  Check admin dashboard or create with different email")
            return None
    except Exception as e:
        print(f"[FAIL] Error creating API key: {e}")
        return None

def test_expirations_endpoint(api_key):
    """Test expirations endpoint with API key"""
    if not api_key:
        print("\n⚠️  Skipping expirations test - no API key")
        return
    
    print(f"\nTesting /api/v1/expirations endpoint with API key...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/expirations",
            headers={"X-API-Key": api_key},
            params={
                "industry": "biotech",
                "date_range": "next_30_days",
                "limit": 5
            },
            timeout=30  # Longer timeout for USPTO API call
        )
        print(f"[OK] Expirations endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {data.get('count', 0)} patents")
            if data.get('data'):
                print(f"  First patent: {data['data'][0].get('patent_id', 'N/A')}")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"[FAIL] Expirations endpoint failed: {e}")
        print("  (This is expected if USPTO API is not configured)")

def main():
    print("=" * 60)
    print("Patent Alert API - Quick Test")
    print("=" * 60)
    
    # Test basic endpoints
    if not test_health():
        print("\n[ERROR] API is not responding. Make sure the server is running:")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    test_root()
    
    # Create API key
    api_key = create_api_key()
    
    # Test protected endpoint
    test_expirations_endpoint(api_key)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/docs for interactive API docs")
    print("2. Use the API key above to test endpoints")
    print("3. Or use the admin dashboard: streamlit run app/admin/dashboard.py")
    
    if api_key:
        print(f"\nYour API Key: {api_key}")
        print("\nExample curl command:")
        print(f'curl -H "X-API-Key: {api_key}" http://localhost:8000/api/v1/expirations?limit=5')

if __name__ == "__main__":
    main()


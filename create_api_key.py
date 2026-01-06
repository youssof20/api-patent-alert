"""
Quick script to create an API key directly in the database
"""
from app.database import SessionLocal, init_db
from app.models.user import APIKey
from app.utils.helpers import generate_api_key

# Initialize database
init_db()

# Create database session
db = SessionLocal()

try:
    # Check if test key already exists
    existing = db.query(APIKey).filter(
        APIKey.partner_email == "test@example.com"
    ).first()
    
    if existing:
        print("=" * 60)
        print("API Key Already Exists!")
        print("=" * 60)
        print(f"Partner: {existing.partner_name}")
        print(f"Email: {existing.partner_email}")
        print(f"API Key: {existing.key}")
        print(f"Active: {existing.is_active}")
        print("\nTo create a new key, use a different email or")
        print("revoke the existing one via admin dashboard.")
    else:
        # Create new API key
        new_key = generate_api_key()
        api_key = APIKey(
            key=new_key,
            partner_name="Test Partner",
            partner_email="test@example.com",
            is_active=True,
            rate_limit_per_minute=60,
            rate_limit_per_day=10000,
            branding_enabled=True
        )
        
        db.add(api_key)
        db.commit()
        
        print("=" * 60)
        print("API Key Created Successfully!")
        print("=" * 60)
        print(f"Partner: {api_key.partner_name}")
        print(f"Email: {api_key.partner_email}")
        print(f"API Key: {api_key.key}")
        print("\n" + "=" * 60)
        print("SAVE THIS KEY - You'll need it to test the API!")
        print("=" * 60)
        print("\nExample usage:")
        print(f'curl -H "X-API-Key: {api_key.key}" http://localhost:8000/api/v1/expirations?limit=5')
        print("\nOr visit http://localhost:8000/docs and click 'Authorize'")
        print(f"Then enter: {api_key.key}")
        
finally:
    db.close()


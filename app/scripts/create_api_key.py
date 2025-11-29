import sys
import secrets
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import Business, ApiKey

# Create tables
Base.metadata.create_all(bind=engine)

def create_test_api_key(
    business_id: str = "demo_sme_001",
    business_name: str = "Neighborhood Coffee Hub",
    industry: str = "Food & Beverage"
):
    """Create a test business and API key"""
    
    db = SessionLocal()
    
    try:
        # Create or get business
        business = db.query(Business).filter(Business.business_id == business_id).first()
        
        if not business:
            business = Business(
                business_id=business_id,
                name=business_name,
                industry=industry,
                tone="warm, community-focused, friendly"
            )
            db.add(business)
            db.commit()
            print(f"✅ Created business: {business_name}")
        else:
            print(f"✅ Business exists: {business_name}")
        
        # Generate API key
        api_key_string = secrets.token_urlsafe(32)
        
        new_key = ApiKey(
            api_key=api_key_string,
            business_id=business_id,
            is_active=True,
            rate_limit_per_min=10
        )
        db.add(new_key)
        db.commit()
        
        print(f"\n🔑 API Key Created Successfully!")
        print(f"=" * 60)
        print(f"Business ID: {business_id}")
        print(f"API Key: {api_key_string}")
        print(f"Rate Limit: 10 requests/minute")
        print(f"=" * 60)
        print(f"\nUse this in your API requests:")
        print(f'curl -H "X-API-Key: {api_key_string}" ...')
        print(f"\nOr in Swagger UI: Click 'Authorize' and paste the key")
        
        return api_key_string
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_test_api_key()
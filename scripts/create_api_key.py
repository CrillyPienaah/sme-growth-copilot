import sys
import secrets
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models import Business, ApiKey

Base.metadata.create_all(bind=engine)

def create_test_api_key():
    db = SessionLocal()
    try:
        business = Business(
            business_id="demo_sme_001",
            name="Neighborhood Coffee Hub",
            industry="Food & Beverage",
            tone="warm, community-focused, friendly"
        )
        db.add(business)
        db.commit()
        
        api_key_string = secrets.token_urlsafe(32)
        new_key = ApiKey(
            api_key=api_key_string,
            business_id="demo_sme_001",
            is_active=True,
            rate_limit_per_min=10
        )
        db.add(new_key)
        db.commit()
        
        print(f"API Key: {api_key_string}")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_api_key()

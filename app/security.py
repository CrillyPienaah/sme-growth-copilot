from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from .database import get_db
from . import models

# Define the expected header name. FastAPI will look for this key in the request headers.
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(
    api_key: str = Security(API_KEY_HEADER),
    db: Session = Depends(get_db)
):
    """
    Validates the API key found in the X-API-Key header against the database.
    If valid, returns the ApiKey ORM record, which includes the rate limit and business_id.
    """
    if not api_key:
        # If the header is missing entirely
        raise HTTPException(
            status_code=401, detail="Authentication required. Please provide a valid X-API-Key header."
        )
    
    # Check the key against the database
    key_record = db.query(models.ApiKey).filter(
        models.ApiKey.api_key == api_key,
        models.ApiKey.is_active == True
    ).first()

    if not key_record:
        # If the key is not found or is marked inactive
        raise HTTPException(
            status_code=403, detail="Invalid or inactive API Key. Access denied."
        )
    
    # Success: Return the ORM record for use in rate limiting and business linking
    return key_record
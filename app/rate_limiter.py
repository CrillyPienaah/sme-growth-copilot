import time
from typing import Dict, List, Tuple
from fastapi import HTTPException
from . import models

# In-memory dictionary to store request timestamps:
# Key: API Key String (str)
# Value: List of timestamps (floats) for the last minute
REQUEST_TRACKER: Dict[str, List[float]] = {}

# Time window in seconds (1 minute)
TIME_WINDOW = 60 

def check_rate_limit(key_record: models.ApiKey):
    """
    Checks the rate limit based on the value stored in the ApiKey record.
    Raises HTTPException 429 if the limit is exceeded.
    """
    api_key_str = key_record.api_key
    current_time = time.time()
    
    # Initialize list for key if it doesn't exist
    if api_key_str not in REQUEST_TRACKER:
        REQUEST_TRACKER[api_key_str] = []
    
    # 1. Clean up old timestamps (keep only those within the last minute)
    # Filter the list, keeping only timestamps newer than (current_time - TIME_WINDOW)
    REQUEST_TRACKER[api_key_str] = [
        t for t in REQUEST_TRACKER[api_key_str] if t > (current_time - TIME_WINDOW)
    ]
    
    # 2. Check the limit
    current_request_count = len(REQUEST_TRACKER[api_key_str])
    allowed_limit = key_record.rate_limit_per_min
    
    if current_request_count >= allowed_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Allowed: {allowed_limit} requests per minute."
        )
    
    # 3. Record the new request
    REQUEST_TRACKER[api_key_str].append(current_time)
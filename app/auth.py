from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY", "changeme")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key

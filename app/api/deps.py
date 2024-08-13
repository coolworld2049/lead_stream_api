from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader

from app.settings import settings

scheme = APIKeyHeader(name="X-Api-Key")


def api_key_auth(api_key: str = Depends(scheme)):
    if api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )

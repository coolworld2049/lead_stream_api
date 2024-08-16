from fastapi import APIRouter

from app.api.endpoints.leads import accept, send

api_router = APIRouter(prefix="/api")
api_router.include_router(accept.router)
api_router.include_router(send.router)

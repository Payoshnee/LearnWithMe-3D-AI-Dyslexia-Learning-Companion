from fastapi import APIRouter

from app.api.v1.companion import router as companion_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(companion_router)

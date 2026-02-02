"""API router combining all endpoints."""

from fastapi import APIRouter

from .endpoints.dashboard import router as dashboard_router
from .endpoints.health import router as health_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard_router)
api_router.include_router(health_router)

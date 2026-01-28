"""Main API router for Service Template."""

from fastapi import APIRouter

from api.endpoints import health

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Add more routers here:
# api_router.include_router(your_router, prefix="/your-endpoint", tags=["YourTag"])

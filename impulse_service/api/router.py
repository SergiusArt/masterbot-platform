"""Main API router for Impulse Service."""

from fastapi import APIRouter

from api.endpoints import analytics, reports, signals, notifications

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(signals.router, prefix="/signals", tags=["Signals"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

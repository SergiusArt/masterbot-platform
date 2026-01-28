"""Main API router."""

from fastapi import APIRouter

from api.endpoints import signals, analytics, reports, notifications

router = APIRouter(prefix="/api/v1")

router.include_router(signals.router)
router.include_router(analytics.router)
router.include_router(reports.router)
router.include_router(notifications.router)

"""Main API router."""

from fastapi import APIRouter

from api.endpoints import signals, notifications

router = APIRouter(prefix="/api/v1")

router.include_router(signals.router)
router.include_router(notifications.router)

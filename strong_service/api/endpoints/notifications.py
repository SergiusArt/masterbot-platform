"""Strong Signal notification settings endpoints."""

from fastapi import APIRouter

from shared.database.connection import async_session_maker
from services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/{user_id}")
async def get_user_settings(user_id: int):
    """Get user notification settings."""
    async with async_session_maker() as session:
        settings = await notification_service.get_user_settings(session, user_id)
        return {
            "user_id": settings.user_id,
            "notifications_enabled": settings.notifications_enabled,
            "long_signals": settings.long_signals,
            "short_signals": settings.short_signals,
            "timezone": settings.timezone,
        }


@router.put("/{user_id}")
async def update_user_settings(user_id: int, updates: dict):
    """Update user notification settings."""
    async with async_session_maker() as session:
        settings = await notification_service.update_user_settings(
            session, user_id, updates
        )
        return {
            "user_id": settings.user_id,
            "notifications_enabled": settings.notifications_enabled,
            "long_signals": settings.long_signals,
            "short_signals": settings.short_signals,
            "timezone": settings.timezone,
        }

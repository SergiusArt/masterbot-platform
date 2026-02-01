"""Notifications API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/{user_id}")
async def get_user_settings(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get user notification settings."""
    settings = await notification_service.get_user_settings(session, user_id)

    return {
        "user_id": settings.user_id,
        "notifications_enabled": settings.notifications_enabled,
        "min_quality": settings.min_quality,
        "min_strength": settings.min_strength,
        "timeframe_1m": settings.timeframe_1m,
        "timeframe_5m": settings.timeframe_5m,
        "timeframe_15m": settings.timeframe_15m,
        "timeframe_30m": settings.timeframe_30m,
        "timeframe_1h": settings.timeframe_1h,
        "long_signals": settings.long_signals,
        "short_signals": settings.short_signals,
        "morning_report": settings.morning_report,
        "evening_report": settings.evening_report,
        "weekly_report": settings.weekly_report,
        "monthly_report": settings.monthly_report,
    }


@router.put("/{user_id}")
async def update_user_settings(
    user_id: int,
    updates: dict,
    session: AsyncSession = Depends(get_db_session),
):
    """Update user notification settings."""
    settings = await notification_service.update_user_settings(
        session, user_id, updates
    )

    return {
        "status": "ok",
        "user_id": settings.user_id,
        "updated": True,
    }

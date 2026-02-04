"""Notifications API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from services.notification_service import notification_service
from shared.utils.logger import get_logger
from shared.utils.redis_client import get_redis_client
from shared.utils.error_publisher import publish_error

logger = get_logger("bablo_notifications_api")

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/{user_id}")
async def get_user_settings(
    user_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get user notification settings."""
    try:
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
            "activity_window_minutes": settings.activity_window_minutes,
            "activity_threshold": settings.activity_threshold,
        }
    except Exception as e:
        logger.error(f"Error getting settings for user {user_id}: {e}", exc_info=True)
        try:
            redis = await get_redis_client()
            await publish_error(redis, "bablo_service", e, context="get_user_settings", user_id=user_id)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}")
async def update_user_settings(
    user_id: int,
    updates: dict,
    session: AsyncSession = Depends(get_db_session),
):
    """Update user notification settings."""
    try:
        settings = await notification_service.update_user_settings(
            session, user_id, updates
        )

        return {
            "status": "ok",
            "user_id": settings.user_id,
            "updated": True,
        }
    except Exception as e:
        logger.error(f"Error updating settings for user {user_id}: {e}", exc_info=True)
        try:
            redis = await get_redis_client()
            await publish_error(redis, "bablo_service", e, context="update_user_settings", user_id=user_id)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_type}/users")
async def get_users_for_report(
    report_type: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Get users subscribed to specific report type.

    Args:
        report_type: Report type (morning, evening, weekly, monthly)

    Returns:
        List of user IDs
    """
    if report_type not in ["morning", "evening", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid report type")

    users = await notification_service.get_users_for_report(session, report_type)
    return {"users": users}

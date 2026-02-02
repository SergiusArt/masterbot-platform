"""Notifications settings API endpoints."""

from fastapi import APIRouter, HTTPException

from services.notification_service import notification_service
from shared.schemas.impulse import NotificationSettingsSchema, NotificationSettingsUpdate

router = APIRouter()


@router.get("/{user_id}", response_model=NotificationSettingsSchema)
async def get_user_settings(user_id: int):
    """Get notification settings for user.

    Args:
        user_id: Telegram user ID

    Returns:
        User notification settings
    """
    try:
        settings = await notification_service.get_settings(user_id)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=NotificationSettingsSchema)
async def update_user_settings(user_id: int, settings: NotificationSettingsUpdate):
    """Update notification settings for user.

    Args:
        user_id: Telegram user ID
        settings: Settings to update

    Returns:
        Updated settings
    """
    try:
        updated = await notification_service.update_settings(user_id, settings)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_type}/users")
async def get_users_for_report(report_type: str):
    """Get users subscribed to specific report type.

    Args:
        report_type: Report type (morning, evening, weekly, monthly)

    Returns:
        List of user IDs
    """
    if report_type not in ["morning", "evening", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid report type")

    try:
        users = await notification_service.get_users_for_report(report_type)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

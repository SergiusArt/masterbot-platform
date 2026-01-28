"""Notification settings service."""

from datetime import time

from sqlalchemy import select

from models.impulse import UserNotificationSettings
from shared.database.connection import async_session_maker
from shared.schemas.impulse import NotificationSettingsSchema, NotificationSettingsUpdate
from shared.utils.logger import get_logger

logger = get_logger("notification_service")


class NotificationService:
    """Service for managing user notification settings."""

    async def get_settings(self, user_id: int) -> NotificationSettingsSchema:
        """Get notification settings for user.

        Args:
            user_id: Telegram user ID

        Returns:
            User notification settings
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(UserNotificationSettings).where(
                    UserNotificationSettings.user_id == user_id
                )
            )
            settings = result.scalar_one_or_none()

            if not settings:
                # Create default settings
                settings = UserNotificationSettings(user_id=user_id)
                session.add(settings)
                await session.commit()
                await session.refresh(settings)

            return NotificationSettingsSchema(
                user_id=settings.user_id,
                growth_threshold=settings.growth_threshold,
                fall_threshold=settings.fall_threshold,
                morning_report=settings.morning_report,
                morning_report_time=settings.morning_report_time,
                evening_report=settings.evening_report,
                evening_report_time=settings.evening_report_time,
                weekly_report=settings.weekly_report,
                monthly_report=settings.monthly_report,
                activity_window_minutes=settings.activity_window_minutes,
                activity_threshold=settings.activity_threshold,
            )

    async def update_settings(
        self,
        user_id: int,
        updates: NotificationSettingsUpdate,
    ) -> NotificationSettingsSchema:
        """Update notification settings for user.

        Args:
            user_id: Telegram user ID
            updates: Settings to update

        Returns:
            Updated settings
        """
        async with async_session_maker() as session:
            result = await session.execute(
                select(UserNotificationSettings).where(
                    UserNotificationSettings.user_id == user_id
                )
            )
            settings = result.scalar_one_or_none()

            if not settings:
                settings = UserNotificationSettings(user_id=user_id)
                session.add(settings)

            # Update only provided fields
            update_data = updates.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(settings, field, value)

            await session.commit()
            await session.refresh(settings)

            logger.info(f"Updated settings for user {user_id}: {update_data}")

            return NotificationSettingsSchema(
                user_id=settings.user_id,
                growth_threshold=settings.growth_threshold,
                fall_threshold=settings.fall_threshold,
                morning_report=settings.morning_report,
                morning_report_time=settings.morning_report_time,
                evening_report=settings.evening_report,
                evening_report_time=settings.evening_report_time,
                weekly_report=settings.weekly_report,
                monthly_report=settings.monthly_report,
                activity_window_minutes=settings.activity_window_minutes,
                activity_threshold=settings.activity_threshold,
            )

    async def get_users_for_alert(
        self,
        impulse_percent: float,
        impulse_type: str,
    ) -> list[int]:
        """Get users who should receive alert for this impulse.

        Args:
            impulse_percent: Impulse percentage
            impulse_type: Impulse type (growth/fall)

        Returns:
            List of user IDs to notify
        """
        async with async_session_maker() as session:
            if impulse_type == "growth":
                query = select(UserNotificationSettings.user_id).where(
                    UserNotificationSettings.growth_threshold <= impulse_percent
                )
            else:
                query = select(UserNotificationSettings.user_id).where(
                    UserNotificationSettings.fall_threshold >= impulse_percent
                )

            result = await session.execute(query)
            return [row[0] for row in result.all()]


# Global service instance
notification_service = NotificationService()

"""Notification service for Bablo user settings."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.bablo import BabloUserSettings
from shared.utils.logger import get_logger

logger = get_logger("bablo_notification_service")


class NotificationService:
    """Service for managing user notification settings."""

    async def get_user_settings(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> BabloUserSettings:
        """Get user settings, create default if not exists.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            BabloUserSettings instance
        """
        query = select(BabloUserSettings).where(BabloUserSettings.user_id == user_id)
        result = await session.execute(query)
        settings = result.scalar_one_or_none()

        if not settings:
            settings = BabloUserSettings(user_id=user_id)
            session.add(settings)
            await session.commit()
            await session.refresh(settings)
            logger.info(f"Created default settings for user {user_id}")

        return settings

    async def update_user_settings(
        self,
        session: AsyncSession,
        user_id: int,
        updates: dict,
    ) -> BabloUserSettings:
        """Update user settings.

        Args:
            session: Database session
            user_id: User ID
            updates: Dictionary of fields to update

        Returns:
            Updated BabloUserSettings instance
        """
        settings = await self.get_user_settings(session, user_id)

        for key, value in updates.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        await session.commit()
        await session.refresh(settings)

        logger.info(f"Updated settings for user {user_id}: {updates}")
        return settings

    async def get_users_for_notification(
        self,
        session: AsyncSession,
        direction: str,
        timeframe: str,
        quality: int,
        strength: int,
    ) -> list[int]:
        """Get users who should receive notification for given signal.

        Args:
            session: Database session
            direction: Signal direction ('long' or 'short')
            timeframe: Signal timeframe
            quality: Signal quality score
            strength: Signal strength (1-5) - not used for filtering

        Returns:
            List of user IDs
        """
        query = select(BabloUserSettings.user_id).where(
            BabloUserSettings.notifications_enabled == True,
            BabloUserSettings.min_quality <= quality,
        )

        # Direction filter
        if direction == "long":
            query = query.where(BabloUserSettings.long_signals == True)
        else:
            query = query.where(BabloUserSettings.short_signals == True)

        # Timeframe filter
        tf_column = getattr(BabloUserSettings, f"timeframe_{timeframe}", None)
        if tf_column is not None:
            query = query.where(tf_column == True)
        else:
            # If timeframe column doesn't exist, don't send notifications
            # This prevents sending signals for unsupported timeframes
            logger.warning(f"Unsupported timeframe: {timeframe}, skipping notifications")
            return []

        result = await session.execute(query)
        return [row[0] for row in result.all()]

    async def get_users_for_report(
        self,
        session: AsyncSession,
        report_type: str,
    ) -> list[int]:
        """Get users subscribed to specific report type.

        Args:
            session: Database session
            report_type: Report type ('morning', 'evening', 'weekly', 'monthly')

        Returns:
            List of user IDs
        """
        report_field = f"{report_type}_report"

        query = select(BabloUserSettings.user_id).where(
            getattr(BabloUserSettings, report_field) == True
        )

        result = await session.execute(query)
        return [row[0] for row in result.all()]

    async def get_users_for_activity_alert(
        self,
        session: AsyncSession,
        signal_count: int,
    ) -> dict[int, tuple[int, int]]:
        """Get users who should receive activity alert.

        Args:
            session: Database session
            signal_count: Current signal count in the window

        Returns:
            Dictionary mapping user_id to (threshold, window_minutes)
        """
        query = select(
            BabloUserSettings.user_id,
            BabloUserSettings.activity_threshold,
            BabloUserSettings.activity_window_minutes,
        ).where(
            BabloUserSettings.notifications_enabled == True,
            BabloUserSettings.activity_threshold > 0,
            BabloUserSettings.activity_threshold <= signal_count,
        )

        result = await session.execute(query)
        return {row[0]: (row[1], row[2]) for row in result.all()}


# Global service instance
notification_service = NotificationService()

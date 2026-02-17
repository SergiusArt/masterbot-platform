"""Strong Signal notification service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.strong import StrongUserSettings
from shared.utils.logger import get_logger

logger = get_logger("strong_notification_service")


class NotificationService:
    """Service for managing Strong Signal user notifications."""

    async def get_users_for_notification(
        self,
        session: AsyncSession,
        direction: str,
    ) -> list[int]:
        """Get users who should receive notification for this signal.

        Args:
            session: Database session
            direction: Signal direction (long/short)

        Returns:
            List of user IDs
        """
        query = select(StrongUserSettings.user_id).where(
            StrongUserSettings.notifications_enabled == True,  # noqa: E712
        )

        if direction == "long":
            query = query.where(StrongUserSettings.long_signals == True)  # noqa: E712
        elif direction == "short":
            query = query.where(StrongUserSettings.short_signals == True)  # noqa: E712

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_user_settings(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> StrongUserSettings:
        """Get or create user notification settings.

        Args:
            session: Database session
            user_id: Telegram user ID

        Returns:
            StrongUserSettings instance
        """
        result = await session.execute(
            select(StrongUserSettings).where(StrongUserSettings.user_id == user_id)
        )
        user_settings = result.scalar_one_or_none()

        if not user_settings:
            user_settings = StrongUserSettings(user_id=user_id)
            session.add(user_settings)
            await session.commit()
            await session.refresh(user_settings)

        return user_settings

    async def update_user_settings(
        self,
        session: AsyncSession,
        user_id: int,
        updates: dict,
    ) -> StrongUserSettings:
        """Update user notification settings.

        Args:
            session: Database session
            user_id: Telegram user ID
            updates: Dictionary of settings to update

        Returns:
            Updated StrongUserSettings instance
        """
        user_settings = await self.get_user_settings(session, user_id)

        allowed_fields = {
            "notifications_enabled",
            "long_signals",
            "short_signals",
            "timezone",
        }

        for key, value in updates.items():
            if key in allowed_fields:
                setattr(user_settings, key, value)

        await session.commit()
        await session.refresh(user_settings)
        return user_settings


# Global instance
notification_service = NotificationService()

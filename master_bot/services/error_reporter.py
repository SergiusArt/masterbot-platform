"""Error reporter service for notifying admin about errors."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from aiogram import Bot

from config import settings

logger = logging.getLogger(__name__)

# Singleton instance
_error_reporter: Optional["ErrorReporter"] = None


class ErrorReporter:
    """Service for reporting errors to admin."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.admin_id = settings.ADMIN_ID
        self._cooldown: dict[str, datetime] = {}
        self._cooldown_seconds = 60  # Don't spam same error type

    async def report(
        self,
        error: Exception,
        user_id: Optional[int] = None,
        context: Optional[str] = None,
    ) -> None:
        """Report error to admin.

        Args:
            error: The exception that occurred
            user_id: User ID who triggered the error (if applicable)
            context: Additional context (e.g., handler name, action)
        """
        try:
            # Create cooldown key to avoid spamming
            error_type = type(error).__name__
            cooldown_key = f"{error_type}:{context or 'unknown'}"

            # Check cooldown
            now = datetime.now()
            last_report = self._cooldown.get(cooldown_key)
            if last_report:
                elapsed = (now - last_report).total_seconds()
                if elapsed < self._cooldown_seconds:
                    logger.debug(f"Skipping error report (cooldown): {cooldown_key}")
                    return

            self._cooldown[cooldown_key] = now

            # Build error message
            parts = ["⚠️ <b>Ошибка в боте</b>\n"]

            if user_id:
                parts.append(f"👤 User ID: <code>{user_id}</code>")

            if context:
                parts.append(f"📍 Место: <code>{context}</code>")

            parts.append(f"❌ Тип: <code>{error_type}</code>")
            parts.append(f"📝 Описание: <code>{str(error)[:500]}</code>")
            parts.append(f"\n🕐 Время: {now.strftime('%Y-%m-%d %H:%M:%S')}")

            message = "\n".join(parts)

            await self.bot.send_message(self.admin_id, message)
            logger.info(f"Error reported to admin: {error_type} for user {user_id}")

        except Exception as e:
            # Don't fail if we can't report - just log
            logger.warning(f"Failed to report error to admin: {e}")


def init_error_reporter(bot: Bot) -> ErrorReporter:
    """Initialize error reporter singleton.

    Args:
        bot: Bot instance

    Returns:
        ErrorReporter instance
    """
    global _error_reporter
    _error_reporter = ErrorReporter(bot)
    return _error_reporter


def get_error_reporter() -> Optional[ErrorReporter]:
    """Get error reporter instance.

    Returns:
        ErrorReporter instance or None if not initialized
    """
    return _error_reporter


async def report_error(
    error: Exception,
    user_id: Optional[int] = None,
    context: Optional[str] = None,
) -> None:
    """Convenience function to report error.

    Args:
        error: The exception that occurred
        user_id: User ID who triggered the error
        context: Additional context
    """
    reporter = get_error_reporter()
    if reporter:
        await reporter.report(error, user_id, context)

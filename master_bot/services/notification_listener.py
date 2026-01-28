"""Redis notification listener for push notifications."""

import asyncio
import json
from typing import Optional

from aiogram import Bot

from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.constants import (
    REDIS_CHANNEL_NOTIFICATIONS,
    EVENT_IMPULSE_ALERT,
    EVENT_ACTIVITY_ALERT,
    EVENT_REPORT_READY,
)

logger = get_logger("notification_listener")


class NotificationListener:
    """Listener for Redis pub/sub notifications."""

    def __init__(self, bot: Bot):
        """Initialize listener.

        Args:
            bot: Telegram bot instance
        """
        self.bot = bot
        self._running = False

    async def start(self) -> None:
        """Start listening for notifications."""
        self._running = True
        logger.info("Starting notification listener...")

        try:
            redis = await get_redis_client()
            pubsub = await redis.subscribe(REDIS_CHANNEL_NOTIFICATIONS)

            async for message in pubsub.listen():
                if not self._running:
                    break

                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                    await self._handle_notification(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in notification: {message['data']}")
                except Exception as e:
                    logger.error(f"Error handling notification: {e}")

        except Exception as e:
            logger.error(f"Notification listener error: {e}")
            if self._running:
                # Reconnect after delay
                await asyncio.sleep(5)
                asyncio.create_task(self.start())

    async def stop(self) -> None:
        """Stop listening for notifications."""
        self._running = False
        logger.info("Notification listener stopped.")

    async def _handle_notification(self, data: dict) -> None:
        """Handle incoming notification.

        Args:
            data: Notification data
        """
        event = data.get("event")
        user_id = data.get("user_id")
        event_data = data.get("data", {})

        if not event or not user_id:
            return

        if event == EVENT_IMPULSE_ALERT:
            await self._send_impulse_alert(user_id, event_data)
        elif event == EVENT_ACTIVITY_ALERT:
            await self._send_activity_alert(user_id, event_data)
        elif event == EVENT_REPORT_READY:
            await self._send_report(user_id, event_data)

    async def _send_impulse_alert(self, user_id: int, data: dict) -> None:
        """Send impulse alert to user.

        Args:
            user_id: Telegram user ID
            data: Impulse data
        """
        symbol = data.get("symbol", "N/A")
        percent = data.get("percent", 0)
        impulse_type = data.get("type", "growth")

        if impulse_type == "growth":
            emoji = "🟢"
            direction = "рост"
        else:
            emoji = "🔴"
            direction = "падение"

        text = (
            f"{emoji} <b>Импульс: {symbol}</b>\n\n"
            f"Тип: {direction}\n"
            f"Изменение: <b>{percent:+.2f}%</b>"
        )

        try:
            await self.bot.send_message(user_id, text)
        except Exception as e:
            logger.error(f"Failed to send impulse alert to {user_id}: {e}")

    async def _send_activity_alert(self, user_id: int, data: dict) -> None:
        """Send activity alert to user.

        Args:
            user_id: Telegram user ID
            data: Activity data
        """
        count = data.get("count", 0)
        window = data.get("window_minutes", 15)

        text = (
            f"⚡ <b>Высокая активность рынка!</b>\n\n"
            f"За последние {window} минут зафиксировано "
            f"<b>{count}</b> импульсов.\n\n"
            f"Рекомендуется проверить ситуацию на рынке."
        )

        try:
            await self.bot.send_message(user_id, text)
        except Exception as e:
            logger.error(f"Failed to send activity alert to {user_id}: {e}")

    async def _send_report(self, user_id: int, data: dict) -> None:
        """Send report to user.

        Args:
            user_id: Telegram user ID
            data: Report data
        """
        text = data.get("text", "Отчёт недоступен")

        try:
            await self.bot.send_message(user_id, text)
        except Exception as e:
            logger.error(f"Failed to send report to {user_id}: {e}")

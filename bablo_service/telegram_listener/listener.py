"""Telegram channel listener for Bablo signals."""

import asyncio
import json
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import settings
from core.parser import bablo_parser
from services.signal_service import signal_service
from services.notification_service import notification_service
from shared.database.connection import async_session_maker
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger

logger = get_logger("bablo_listener")

REDIS_CHANNEL = "bablo:notifications"
EVENT_BABLO_SIGNAL = "bablo_signal"


class BabloTelegramListener:
    """Listener for Bablo Telegram channel."""

    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self._running = False

    async def start(self) -> None:
        """Start listening to channel."""
        if not settings.TELEGRAM_SESSION_STRING:
            logger.warning("No Telegram session string configured, skipping listener")
            return

        try:
            self.client = TelegramClient(
                StringSession(settings.TELEGRAM_SESSION_STRING),
                settings.TELEGRAM_API_ID,
                settings.TELEGRAM_API_HASH,
            )

            await self.client.start()
            self._running = True

            # Register handler for new messages
            @self.client.on(events.NewMessage(chats=[settings.BABLO_CHANNEL_ID]))
            async def handler(event):
                await self._handle_message(event)

            logger.info(f"Bablo listener started for channel {settings.BABLO_CHANNEL_ID}")

            # Keep running
            while self._running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Listener error: {e}")
            await asyncio.sleep(10)
            if self._running:
                await self.start()

    async def stop(self) -> None:
        """Stop listening."""
        self._running = False
        if self.client:
            await self.client.disconnect()
            logger.info("Bablo listener stopped")

    async def _handle_message(self, event) -> None:
        """Handle incoming message."""
        message = event.message
        if not message.text:
            return

        # Parse message
        signal_data = bablo_parser.parse(message.text)
        if not signal_data:
            return

        try:
            # Save to database
            async with async_session_maker() as session:
                signal = await signal_service.create_signal(
                    session,
                    signal_data,
                    telegram_message_id=message.id,
                )

                # Get users to notify
                users = await notification_service.get_users_for_notification(
                    session,
                    direction=signal_data.direction,
                    timeframe=signal_data.timeframe,
                    quality=signal_data.quality_total,
                    strength=signal_data.strength,
                )

            # Publish notifications
            if users:
                await self._publish_notifications(signal_data, users)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _publish_notifications(self, signal_data, user_ids: list[int]) -> None:
        """Publish notifications to Redis for users."""
        redis = await get_redis_client()

        # Format signal message
        direction_emoji = "🟢" if signal_data.direction == "long" else "🔴"
        direction_text = "Long" if signal_data.direction == "long" else "Short"
        strength_squares = "🟩" * signal_data.strength if signal_data.direction == "long" else "🟥" * signal_data.strength

        message_text = (
            f"{strength_squares} <b>{signal_data.symbol}</b>\n"
            f"{direction_emoji} {direction_text} | {signal_data.timeframe} ТФ\n"
            f"⭐ Качество: {signal_data.quality_total}/10\n"
        )

        if signal_data.max_drawdown:
            message_text += f"📉 Макс. просадка: {signal_data.max_drawdown}%"

        for user_id in user_ids:
            notification = {
                "event": EVENT_BABLO_SIGNAL,
                "user_id": user_id,
                "data": {
                    "symbol": signal_data.symbol,
                    "direction": signal_data.direction,
                    "strength": signal_data.strength,
                    "timeframe": signal_data.timeframe,
                    "quality": signal_data.quality_total,
                    "message": message_text,
                },
            }

            await redis.publish(REDIS_CHANNEL, json.dumps(notification))

        logger.info(f"Published notification to {len(user_ids)} users")


# Global listener instance
bablo_listener = BabloTelegramListener()

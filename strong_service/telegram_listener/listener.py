"""Telegram channel listener for Strong Signal."""

import asyncio
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import settings
from core.parser import strong_parser
from services.signal_service import signal_service
from services.notification_service import notification_service
from shared.database.connection import async_session_maker
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.utils.error_publisher import publish_error
from shared.constants import EVENT_STRONG_SIGNAL, REDIS_CHANNEL_STRONG

logger = get_logger("strong_listener")


class StrongTelegramListener:
    """Listener for Strong Signal Telegram channel."""

    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self._running = False

    async def start(self) -> None:
        """Start listening to channel."""
        logger.info("Initializing Strong Signal Telegram listener...")

        if not settings.TELEGRAM_SESSION_STRING:
            logger.warning("No Telegram session string configured, skipping listener")
            return

        try:
            logger.info("Creating Telegram client for Strong Signal...")
            self.client = TelegramClient(
                StringSession(settings.TELEGRAM_SESSION_STRING),
                settings.TELEGRAM_API_ID,
                settings.TELEGRAM_API_HASH,
            )

            logger.info("Connecting to Telegram...")
            await self.client.start()
            self._running = True
            logger.info("Telegram client connected successfully!")

            @self.client.on(events.NewMessage(chats=[settings.STRONG_CHANNEL_ID]))
            async def handler(event):
                logger.info(f"🔥 STRONG HANDLER TRIGGERED! Chat: {event.chat_id}")
                await self._handle_message(event)

            logger.info(f"✅ Strong listener started for channel {settings.STRONG_CHANNEL_ID}")

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
            logger.info("Strong listener stopped")

    async def _handle_message(self, event) -> None:
        """Handle incoming message."""
        logger.info(f"📩 Processing Strong message from chat {event.chat_id}")
        message = event.message
        if not message.text:
            logger.debug("Message has no text, skipping")
            return

        logger.info(f"📝 Strong message text: {message.text[:200]}")

        signal_data = strong_parser.parse(message.text)
        if not signal_data:
            logger.info("⚠️ Strong parser could not recognize signal format")
            return

        logger.info(f"✅ Parsed Strong signal: {signal_data.symbol} {signal_data.direction}")

        try:
            async with async_session_maker() as session:
                signal = await signal_service.create_signal(
                    session,
                    signal_data,
                    telegram_message_id=message.id,
                )

                users = await notification_service.get_users_for_notification(
                    session,
                    direction=signal_data.direction,
                )

            if users:
                await self._publish_notifications(signal_data, users)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            try:
                redis = await get_redis_client()
                await publish_error(redis, "strong_service", e, context="handle_message")
            except Exception:
                pass

    async def _publish_notifications(
        self, signal_data, user_ids: list[int]
    ) -> None:
        """Publish notifications to Redis for users."""
        redis = await get_redis_client()

        messages = [
            {
                "event": EVENT_STRONG_SIGNAL,
                "user_id": user_id,
                "data": {
                    "symbol": signal_data.symbol,
                    "direction": signal_data.direction,
                },
            }
            for user_id in user_ids
        ]

        await redis.publish_batch(REDIS_CHANNEL_STRONG, messages)
        logger.info(f"Published notification to {len(user_ids)} users")


# Global listener instance
strong_listener = StrongTelegramListener()

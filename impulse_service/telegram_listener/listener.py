"""Telegram channel listener using Telethon."""

import asyncio
import traceback
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from core.parser import impulse_parser
from services.signal_service import signal_service
from services.notification_service import notification_service
from shared.schemas.impulse import ImpulseCreate
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.constants import REDIS_CHANNEL_NOTIFICATIONS, EVENT_IMPULSE_ALERT
from config import settings

logger = get_logger("telegram_listener")


class TelegramListener:
    """Listener for Telegram channel messages."""

    def __init__(self):
        self._client: Optional[TelegramClient] = None
        self._running = False

    async def start(self) -> None:
        """Start listening to Telegram channel."""
        logger.info("Initializing Telegram listener...")

        # Log credentials status (without revealing values)
        logger.info(f"TELEGRAM_API_ID present: {bool(settings.TELEGRAM_API_ID)}")
        logger.info(f"TELEGRAM_API_HASH present: {bool(settings.TELEGRAM_API_HASH)}")
        logger.info(f"TELEGRAM_SESSION_STRING present: {bool(settings.TELEGRAM_SESSION_STRING)}")
        logger.info(f"SOURCE_CHANNEL_ID: {settings.SOURCE_CHANNEL_ID}")

        if not settings.TELEGRAM_API_ID or not settings.TELEGRAM_API_HASH:
            logger.warning("Telegram API credentials not configured. Listener disabled.")
            return

        if not settings.TELEGRAM_SESSION_STRING:
            logger.warning("Telegram session string not configured. Listener disabled.")
            return

        if not settings.SOURCE_CHANNEL_ID:
            logger.warning("Source channel ID not configured. Listener disabled.")
            return

        self._running = True
        logger.info(f"Starting Telegram listener for channel {settings.SOURCE_CHANNEL_ID}...")

        try:
            logger.info("Creating Telegram client...")
            logger.info(f"Session string length: {len(settings.TELEGRAM_SESSION_STRING)}")

            self._client = TelegramClient(
                StringSession(settings.TELEGRAM_SESSION_STRING),
                settings.TELEGRAM_API_ID,
                settings.TELEGRAM_API_HASH,
            )
            logger.info("Telegram client object created successfully")

            logger.info("Connecting to Telegram (this may take a few seconds)...")
            try:
                await asyncio.wait_for(self._client.start(), timeout=30.0)
                logger.info("Telegram client connected successfully!")
            except asyncio.TimeoutError:
                logger.error("Timeout while connecting to Telegram (30 seconds)")
                raise

            # Register message handler
            logger.info(f"Registering message handler for channel {settings.SOURCE_CHANNEL_ID}...")

            @self._client.on(events.NewMessage(chats=[settings.SOURCE_CHANNEL_ID]))
            async def handler(event):
                logger.info(f"🔥 HANDLER TRIGGERED! Chat: {event.chat_id}")
                await self._handle_message(event)

            logger.info(f"✅ Listening to channel: {settings.SOURCE_CHANNEL_ID}")
            logger.info("Handler is now active and waiting for messages...")

            # Keep running
            while self._running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Telegram listener error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            if self._running:
                # Reconnect after delay
                logger.info("Will attempt to reconnect in 10 seconds...")
                await asyncio.sleep(10)
                asyncio.create_task(self.start())

    async def stop(self) -> None:
        """Stop the listener."""
        self._running = False
        if self._client:
            await self._client.disconnect()
        logger.info("Telegram listener stopped.")

    async def _handle_message(self, event) -> None:
        """Handle incoming message from channel.

        Args:
            event: Telethon event
        """
        try:
            logger.info(f"📩 Processing message from chat {event.chat_id}")
            message_text = event.message.message
            if not message_text:
                logger.debug("Message has no text, skipping")
                return

            logger.info(f"📝 Message text: {message_text[:200]}")

            # Parse the message
            parsed = impulse_parser.parse(message_text)
            if not parsed:
                logger.info(f"⚠️ Parser could not recognize impulse format")
                return

            logger.info(f"Parsed impulse: {parsed.symbol} {parsed.percent}%")

            # Create impulse in database
            impulse_create = ImpulseCreate(
                symbol=parsed.symbol,
                percent=parsed.percent,
                max_percent=parsed.max_percent,
                type=parsed.type,
                growth_ratio=parsed.growth_ratio,
                fall_ratio=parsed.fall_ratio,
                raw_message=message_text,
            )

            await signal_service.create_signal(impulse_create)

            # Send notifications to users
            await self._send_notifications(parsed)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _send_notifications(self, parsed) -> None:
        """Send notifications to users who match the threshold.

        Args:
            parsed: Parsed impulse data
        """
        try:
            user_ids = await notification_service.get_users_for_alert(
                float(parsed.percent),
                parsed.type,
            )

            if not user_ids:
                return

            redis = await get_redis_client()

            for user_id in user_ids:
                await redis.publish(
                    REDIS_CHANNEL_NOTIFICATIONS,
                    {
                        "event": EVENT_IMPULSE_ALERT,
                        "user_id": user_id,
                        "data": {
                            "symbol": parsed.symbol,
                            "percent": float(parsed.percent),
                            "type": parsed.type,
                        },
                    },
                )

            logger.info(f"Sent impulse alert to {len(user_ids)} users")

        except Exception as e:
            logger.error(f"Error sending notifications: {e}")

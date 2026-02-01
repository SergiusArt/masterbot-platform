"""Telegram channel listener for Bablo signals."""

import asyncio
from datetime import datetime, timedelta
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
from shared.constants import EVENT_BABLO_SIGNAL, EVENT_BABLO_ACTIVITY

logger = get_logger("bablo_listener")

REDIS_CHANNEL = "bablo:notifications"


class BabloTelegramListener:
    """Listener for Bablo Telegram channel."""

    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self._running = False

    async def start(self) -> None:
        """Start listening to channel."""
        logger.info("Initializing Bablo Telegram listener...")

        if not settings.TELEGRAM_SESSION_STRING:
            logger.warning("No Telegram session string configured, skipping listener")
            return

        try:
            logger.info("Creating Telegram client for Bablo...")
            self.client = TelegramClient(
                StringSession(settings.TELEGRAM_SESSION_STRING),
                settings.TELEGRAM_API_ID,
                settings.TELEGRAM_API_HASH,
            )

            logger.info("Connecting to Telegram...")
            await self.client.start()
            self._running = True
            logger.info("Telegram client connected successfully!")

            # Register handler for new messages
            @self.client.on(events.NewMessage(chats=[settings.BABLO_CHANNEL_ID]))
            async def handler(event):
                logger.info(f"🔥 BABLO HANDLER TRIGGERED! Chat: {event.chat_id}")
                await self._handle_message(event)

            logger.info(f"✅ Bablo listener started for channel {settings.BABLO_CHANNEL_ID}")
            logger.info("Handler is now active and waiting for messages...")

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
        logger.info(f"📩 Processing Bablo message from chat {event.chat_id}")
        message = event.message
        if not message.text:
            logger.debug("Message has no text, skipping")
            return

        logger.info(f"📝 Bablo message text: {message.text[:200]}")

        # Parse message
        signal_data = bablo_parser.parse(message.text)
        if not signal_data:
            logger.info(f"⚠️ Bablo parser could not recognize signal format")
            return

        logger.info(f"✅ Parsed Bablo signal: {signal_data.symbol} {signal_data.direction} strength={signal_data.strength}")

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
                await self._publish_notifications(signal_data, users, message.text)

            # Check and notify about high activity
            await self._check_and_notify_activity()

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _publish_notifications(self, signal_data, user_ids: list[int], original_text: str) -> None:
        """Publish notifications to Redis for users."""
        redis = await get_redis_client()

        # Use original Telegram message text (from TradingView with Markdown formatting)
        for user_id in user_ids:
            notification = {
                "event": EVENT_BABLO_SIGNAL,
                "user_id": user_id,
                "data": {
                    "symbol": signal_data.symbol,
                    "direction": signal_data.direction,
                    "strength": signal_data.strength,
                    "timeframe": signal_data.timeframe,
                    "quality_total": signal_data.quality_total,
                    "original_text": original_text,
                },
            }

            await redis.publish(REDIS_CHANNEL, notification)

        logger.info(f"Published notification to {len(user_ids)} users")

    async def _check_and_notify_activity(self) -> None:
        """Check for high activity and notify users."""
        try:
            now = datetime.utcnow()

            async with async_session_maker() as session:
                # Count signals in the max possible window (60 min)
                from_time = now - timedelta(minutes=60)
                signal_count = await signal_service.get_signals_count(
                    session,
                    from_date=from_time,
                    to_date=now,
                )

                logger.info(f"Activity check: {signal_count} signals in last 60 min")

                if signal_count == 0:
                    return

                # Get users whose threshold is met
                users_settings = await notification_service.get_users_for_activity_alert(
                    session,
                    signal_count=signal_count,
                )

                if not users_settings:
                    logger.info(f"Activity check: no users with threshold <= {signal_count}")
                    return

                # Check Redis to avoid spamming
                redis = await get_redis_client()
                users_to_notify = []

                for user_id, (threshold, window) in users_settings.items():
                    # Count signals for this user's specific window
                    user_from_time = now - timedelta(minutes=window)
                    user_signal_count = await signal_service.get_signals_count(
                        session,
                        from_date=user_from_time,
                        to_date=now,
                    )

                    if user_signal_count < threshold:
                        continue

                    # Check cooldown
                    redis_key = f"bablo:activity_notified:{user_id}"
                    last_notified = await redis.get(redis_key)

                    if last_notified is not None:
                        continue

                    users_to_notify.append((user_id, threshold, window, user_signal_count))
                    # Set cooldown (half of user's window in seconds)
                    await redis.set(redis_key, "1", expire=window * 30)

                if not users_to_notify:
                    return

                # Publish activity notifications
                for user_id, threshold, window, count in users_to_notify:
                    notification = {
                        "event": EVENT_BABLO_ACTIVITY,
                        "user_id": user_id,
                        "data": {
                            "signal_count": count,
                            "window_minutes": window,
                            "threshold": threshold,
                        },
                    }

                    await redis.publish(REDIS_CHANNEL, notification)

                logger.info(f"📈 Activity alert sent to {len(users_to_notify)} users")

        except Exception as e:
            logger.error(f"Error checking activity: {e}")


# Global listener instance
bablo_listener = BabloTelegramListener()

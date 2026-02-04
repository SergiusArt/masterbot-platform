"""Telegram channel listener using Telethon."""

import asyncio
import traceback
from datetime import datetime, timedelta, timezone
from typing import Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from core.parser import impulse_parser
from services.signal_service import signal_service
from services.notification_service import notification_service
from shared.schemas.impulse import ImpulseCreate
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.utils.error_publisher import publish_error
from shared.constants import REDIS_CHANNEL_NOTIFICATIONS, EVENT_IMPULSE_ALERT, EVENT_ACTIVITY_ALERT
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

            # Check and notify about high activity
            await self._check_and_notify_activity()

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            try:
                redis = await get_redis_client()
                await publish_error(redis, "impulse_service", e, context="handle_message")
            except Exception:
                pass

    async def _send_notifications(self, parsed) -> None:
        """Send notifications to users who match the threshold.

        Uses Redis pipeline for batch publish (1 network call instead of N).

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

            # Build batch of messages
            messages = [
                {
                    "event": EVENT_IMPULSE_ALERT,
                    "user_id": user_id,
                    "data": {
                        "symbol": parsed.symbol,
                        "percent": float(parsed.percent),
                        "type": parsed.type,
                    },
                }
                for user_id in user_ids
            ]

            # Single network call for all publishes
            await redis.publish_batch(REDIS_CHANNEL_NOTIFICATIONS, messages)

            logger.info(f"Sent impulse alert to {len(user_ids)} users")

        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            try:
                redis = await get_redis_client()
                await publish_error(redis, "impulse_service", e, context="send_notifications")
            except Exception:
                pass

    async def _check_and_notify_activity(self) -> None:
        """Check for high activity and notify users.

        Optimized version:
        - Uses MGET to batch-fetch last notification times from Redis
        - Groups COUNT queries by unique time windows to minimize DB calls
        - Uses batch Redis SET for updating notification times

        Logic: count only NEW impulses since last notification.
        After sending alert, remember the timestamp so next time
        only impulses after that point are counted.
        """
        try:
            now = datetime.now(timezone.utc)

            # Get users with activity tracking enabled
            users_settings = await notification_service.get_users_for_activity_alert()

            if not users_settings:
                return

            redis = await get_redis_client()
            user_ids = list(users_settings.keys())

            # Step 1: Batch fetch last notification times (1 Redis call instead of N)
            redis_keys = [f"impulse:activity_last:{uid}" for uid in user_ids]
            last_notified_values = await redis.mget(redis_keys)
            last_notified_map = dict(zip(user_ids, last_notified_values))

            # Step 2: Group users by unique windows and get counts
            # Find unique windows to minimize COUNT queries
            unique_windows = set(window for _, (_, window) in users_settings.items())
            counts_by_window: dict[int, int] = {}

            for window in unique_windows:
                window_start = now - timedelta(minutes=window)
                counts_by_window[window] = await signal_service.get_signals_count(
                    from_date=window_start,
                    to_date=now,
                )

            # Step 3: Check each user against their threshold
            users_to_notify = []
            redis_updates: dict[str, str] = {}

            for user_id, (threshold, window) in users_settings.items():
                window_start = now - timedelta(minutes=window)
                last_notified_str = last_notified_map.get(user_id)

                # Determine count_from based on last notification
                if last_notified_str:
                    try:
                        last_notified_at = datetime.fromisoformat(last_notified_str)
                        count_from = max(window_start, last_notified_at)
                    except ValueError:
                        count_from = window_start
                else:
                    count_from = window_start

                # If user was notified recently, we need individual count
                # Otherwise use the cached window count
                if count_from > window_start:
                    # User was notified within the window - need individual count
                    user_impulse_count = await signal_service.get_signals_count(
                        from_date=count_from,
                        to_date=now,
                    )
                else:
                    # Use cached count for this window
                    user_impulse_count = counts_by_window[window]

                logger.debug(
                    f"Activity check user {user_id}: "
                    f"{user_impulse_count} impulses "
                    f"(threshold={threshold}, window={window}m)"
                )

                if user_impulse_count < threshold:
                    continue

                # Atomic cooldown: use SET NX to prevent race condition
                # Only ONE of parallel _check_activity calls can set this key
                cooldown_key = f"impulse:activity_cooldown:{user_id}"
                can_notify = await redis.client.set(cooldown_key, "1", nx=True, ex=60)
                if not can_notify:
                    logger.debug(
                        f"Skipping activity alert for {user_id}: "
                        f"cooldown (atomic lock exists)"
                    )
                    continue

                users_to_notify.append((user_id, threshold, window, user_impulse_count))
                # Queue Redis update
                redis_key = f"impulse:activity_last:{user_id}"
                redis_updates[redis_key] = now.isoformat()

            if not users_to_notify:
                return

            # Step 4: Batch update Redis (notification times)
            if redis_updates:
                await redis.mset(redis_updates)
                # Set expiration for each key individually (MSET doesn't support TTL)
                for user_id, (_, window) in users_settings.items():
                    redis_key = f"impulse:activity_last:{user_id}"
                    if redis_key in redis_updates:
                        await redis.client.expire(redis_key, window * 60)

            # Step 5: Publish activity notifications (batch)
            messages = [
                {
                    "event": EVENT_ACTIVITY_ALERT,
                    "user_id": user_id,
                    "data": {
                        "count": count,
                        "window_minutes": window,
                        "threshold": threshold,
                    },
                }
                for user_id, threshold, window, count in users_to_notify
            ]
            await redis.publish_batch(REDIS_CHANNEL_NOTIFICATIONS, messages)

            logger.info(f"📈 Activity alert sent to {len(users_to_notify)} users")

        except Exception as e:
            logger.error(f"Error checking activity: {e}", exc_info=True)
            try:
                redis = await get_redis_client()
                await publish_error(redis, "impulse_service", e, context="check_activity")
            except Exception:
                pass

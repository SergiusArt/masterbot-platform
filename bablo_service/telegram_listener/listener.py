"""Telegram channel listener for Bablo signals."""

import asyncio
from datetime import datetime, timedelta, timezone
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
from shared.utils.error_publisher import publish_error
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
            logger.info("Activity check completed")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            try:
                redis = await get_redis_client()
                await publish_error(redis, "bablo_service", e, context="handle_message")
            except Exception:
                pass

    async def _publish_notifications(self, signal_data, user_ids: list[int], original_text: str) -> None:
        """Publish notifications to Redis for users.

        Uses Redis pipeline for batch publish (1 network call instead of N).
        """
        redis = await get_redis_client()

        # Build batch of messages
        messages = [
            {
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
            for user_id in user_ids
        ]

        # Single network call for all publishes
        await redis.publish_batch(REDIS_CHANNEL, messages)

        logger.info(f"Published notification to {len(user_ids)} users")

    async def _check_and_notify_activity(self) -> None:
        """Check for high activity and notify users.

        Optimized version:
        - Uses MGET to batch-fetch last notification times from Redis
        - Groups COUNT queries by unique time windows to minimize DB calls
        - Uses batch Redis SET for updating notification times

        Logic: count only NEW signals since last notification.
        After sending alert, remember the timestamp so next time
        only signals after that point are counted.
        """
        try:
            now = datetime.now(timezone.utc)

            async with async_session_maker() as session:
                # Get users with activity tracking enabled
                users_settings = await notification_service.get_users_for_activity_alert(
                    session,
                    signal_count=999999,  # get all users with threshold > 0
                )

                if not users_settings:
                    return

                redis = await get_redis_client()
                user_ids = list(users_settings.keys())

                # Step 1: Batch fetch last notification times (1 Redis call instead of N)
                redis_keys = [f"bablo:activity_last:{uid}" for uid in user_ids]
                last_notified_values = await redis.mget(redis_keys)
                last_notified_map = dict(zip(user_ids, last_notified_values))

                # Step 2: Group users by unique windows and get counts
                unique_windows = set(window for _, (_, window) in users_settings.items())
                counts_by_window: dict[int, int] = {}

                for window in unique_windows:
                    window_start = now - timedelta(minutes=window)
                    counts_by_window[window] = await signal_service.get_signals_count(
                        session,
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
                        user_signal_count = await signal_service.get_signals_count(
                            session,
                            from_date=count_from,
                            to_date=now,
                        )
                    else:
                        # Use cached count for this window
                        user_signal_count = counts_by_window[window]

                    logger.debug(
                        f"Activity check user {user_id}: "
                        f"{user_signal_count} signals "
                        f"(threshold={threshold}, window={window}m)"
                    )

                    if user_signal_count < threshold:
                        continue

                    # Atomic cooldown: use SET NX to prevent race condition
                    # Only ONE of parallel _check_activity calls can set this key
                    cooldown_key = f"bablo:activity_cooldown:{user_id}"
                    can_notify = await redis.client.set(cooldown_key, "1", nx=True, ex=60)
                    if not can_notify:
                        logger.debug(
                            f"Skipping activity alert for {user_id}: "
                            f"cooldown (atomic lock exists)"
                        )
                        continue

                    users_to_notify.append((user_id, threshold, window, user_signal_count))
                    # Queue Redis update
                    redis_key = f"bablo:activity_last:{user_id}"
                    redis_updates[redis_key] = now.isoformat()

                if not users_to_notify:
                    return

                # Step 4: Batch update Redis (notification times)
                if redis_updates:
                    await redis.mset(redis_updates)
                    # Set expiration for each key individually (MSET doesn't support TTL)
                    for user_id, (_, window) in users_settings.items():
                        redis_key = f"bablo:activity_last:{user_id}"
                        if redis_key in redis_updates:
                            await redis.client.expire(redis_key, window * 60)

                # Step 5: Publish activity notifications (batch)
                messages = [
                    {
                        "event": EVENT_BABLO_ACTIVITY,
                        "user_id": user_id,
                        "data": {
                            "signal_count": count,
                            "window_minutes": window,
                            "threshold": threshold,
                        },
                    }
                    for user_id, threshold, window, count in users_to_notify
                ]
                await redis.publish_batch(REDIS_CHANNEL, messages)

                logger.info(f"📈 Activity alert sent to {len(users_to_notify)} users")

        except BaseException as e:
            logger.error(f"Error checking activity: {type(e).__name__}: {e}", exc_info=True)
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            try:
                redis = await get_redis_client()
                await publish_error(redis, "bablo_service", e, context="check_activity")
            except Exception:
                pass


# Global listener instance
bablo_listener = BabloTelegramListener()

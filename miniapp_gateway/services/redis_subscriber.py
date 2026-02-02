"""Redis pub/sub subscriber for real-time notifications."""

import asyncio
import json
import logging
from typing import Optional

import redis.asyncio as redis

from config import settings
from websocket.manager import (
    ConnectionManager,
    WebSocketMessage,
    WSMessageType,
    connection_manager,
)

logger = logging.getLogger(__name__)


class RedisSubscriber:
    """Subscribes to Redis channels and broadcasts to WebSocket clients."""

    def __init__(
        self,
        redis_url: str = settings.REDIS_URL,
        manager: ConnectionManager = connection_manager,
    ):
        self.redis_url = redis_url
        self.manager = manager
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start subscribing to Redis channels."""
        if self._running:
            logger.warning("Redis subscriber already running")
            return

        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            self._pubsub = self._redis.pubsub()

            # Subscribe to notification channels
            channels = [
                settings.REDIS_CHANNEL_IMPULSE,
                settings.REDIS_CHANNEL_BABLO,
            ]
            await self._pubsub.subscribe(*channels)
            logger.info(f"Subscribed to Redis channels: {channels}")

            self._running = True
            self._task = asyncio.create_task(self._listen())

        except Exception as e:
            logger.error(f"Failed to start Redis subscriber: {e}")
            raise

    async def stop(self) -> None:
        """Stop the subscriber."""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()

        if self._redis:
            await self._redis.close()

        logger.info("Redis subscriber stopped")

    async def _listen(self) -> None:
        """Listen for messages from Redis."""
        logger.info("Starting to listen for Redis messages...")

        try:
            while self._running:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message is not None:
                    await self._handle_message(message)
                await asyncio.sleep(0.01)  # Small sleep to prevent tight loop

        except asyncio.CancelledError:
            logger.info("Redis listener cancelled")
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")
            # Try to reconnect after error
            if self._running:
                await asyncio.sleep(5)
                await self.start()

    async def _handle_message(self, message: dict) -> None:
        """Handle a message from Redis.

        Args:
            message: Redis message dict with 'channel', 'data', 'type' keys
        """
        try:
            channel = message.get("channel", "")
            data = message.get("data", "")

            if not data or message.get("type") != "message":
                return

            # Parse the data
            try:
                payload = json.loads(data) if isinstance(data, str) else data
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from Redis: {data[:100]}")
                return

            # Determine message type based on channel
            if channel == settings.REDIS_CHANNEL_IMPULSE:
                ws_message = WebSocketMessage(
                    type=WSMessageType.IMPULSE_NEW,
                    data=payload,
                )
            elif channel == settings.REDIS_CHANNEL_BABLO:
                ws_message = WebSocketMessage(
                    type=WSMessageType.BABLO_NEW,
                    data=payload,
                )
            else:
                logger.debug(f"Unknown channel: {channel}")
                return

            # Broadcast to all connected clients
            sent_count = await self.manager.broadcast(ws_message)
            logger.debug(
                f"Broadcasted {ws_message.type.value} to {sent_count} clients"
            )

        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")

    @property
    def is_running(self) -> bool:
        """Check if subscriber is running."""
        return self._running


# Global subscriber instance
redis_subscriber = RedisSubscriber()

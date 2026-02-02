"""Redis client for caching and pub/sub."""

import os
import json
from typing import Optional, Any

import redis.asyncio as redis


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._client is None:
            self._client = redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None,
    ) -> bool:
        """Set value with optional expiration."""
        return await self.client.set(key, value, ex=expire)

    async def delete(self, key: str) -> int:
        """Delete key."""
        return await self.client.delete(key)

    async def mget(self, keys: list[str]) -> list[Optional[str]]:
        """Get multiple values by keys (batch operation)."""
        if not keys:
            return []
        return await self.client.mget(keys)

    async def mset(self, mapping: dict[str, str]) -> bool:
        """Set multiple key-value pairs (batch operation)."""
        if not mapping:
            return True
        return await self.client.mset(mapping)

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value by key."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """Set JSON value with optional expiration."""
        return await self.set(key, json.dumps(value), expire)

    async def publish(self, channel: str, message: dict) -> int:
        """Publish message to channel."""
        return await self.client.publish(channel, json.dumps(message))

    async def publish_batch(self, channel: str, messages: list[dict]) -> list[int]:
        """Publish multiple messages to channel using pipeline.

        Uses Redis pipeline to batch publish operations into a single
        network round-trip, significantly reducing latency for multiple
        publishes (e.g., 500 users = 1 call instead of 500).

        Args:
            channel: Redis channel name
            messages: List of message dictionaries to publish

        Returns:
            List of subscriber counts for each publish
        """
        if not messages:
            return []

        async with self.client.pipeline(transaction=False) as pipe:
            for message in messages:
                pipe.publish(channel, json.dumps(message))
            results = await pipe.execute()

        return results

    async def subscribe(self, *channels: str) -> redis.client.PubSub:
        """Subscribe to channels."""
        self._pubsub = self.client.pubsub()
        await self._pubsub.subscribe(*channels)
        return self._pubsub

    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            await self.client.ping()
            return True
        except Exception:
            return False


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get global Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client

"""Throttling middleware to prevent spam."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from shared.utils.redis_client import get_redis_client


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for rate limiting."""

    def __init__(self, rate_limit: float = 0.5):
        """Initialize middleware.

        Args:
            rate_limit: Minimum time between messages in seconds
        """
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Process incoming message."""
        user = event.from_user
        if not user:
            return await handler(event, data)

        user_id = user.id
        key = f"throttle:{user_id}"

        try:
            redis = await get_redis_client()

            # Check if user is throttled
            if await redis.get(key):
                return  # Silently ignore throttled messages

            # Set throttle key with expiration (in seconds, minimum 1)
            await redis.set(key, "1", expire=max(1, int(self.rate_limit)))

        except Exception:
            # If Redis fails, continue without throttling
            pass

        return await handler(event, data)

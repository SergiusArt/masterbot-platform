"""Private chat topic management for Bot API 9.4.

Creates and manages forum topics in private chats,
routing messages to the correct section topic.
"""

import asyncio
import json
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.constants import (
    TOPIC_CONFIG,
    REDIS_KEY_TOPICS,
)

logger = get_logger("topic_manager")


class TopicManager:
    """Manages forum topics in private chats.

    Stores topic thread IDs in Redis for quick lookup.
    Creates topics on first interaction via /start.
    Uses asyncio.Lock per user to prevent race conditions.
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self._locks: dict[int, asyncio.Lock] = {}

    def _get_lock(self, user_id: int) -> asyncio.Lock:
        """Get or create a per-user lock."""
        if user_id not in self._locks:
            self._locks[user_id] = asyncio.Lock()
        return self._locks[user_id]

    async def get_topic_id(
        self, user_id: int, section: str
    ) -> Optional[int]:
        """Get topic thread ID for a user's section.

        Creates topics lazily if they don't exist yet.
        Returns None if topics can't be created.
        """
        topics = await self._get_stored_topics(user_id)
        if section in topics:
            return topics[section]

        # Lazy creation — for existing users who never sent /start
        topics = await self.ensure_topics(user_id)
        return topics.get(section)

    async def has_topics(self, user_id: int) -> bool:
        """Check if topics have been created for a user."""
        topics = await self._get_stored_topics(user_id)
        return len(topics) > 0

    async def ensure_topics(self, user_id: int) -> dict[str, int]:
        """Create topics if they don't exist, return all topic IDs.

        Uses per-user lock to prevent race conditions when
        multiple notifications arrive simultaneously.

        Returns:
            Dict mapping section name to thread_id
        """
        lock = self._get_lock(user_id)
        async with lock:
            return await self._ensure_topics_locked(user_id)

    async def _ensure_topics_locked(self, user_id: int) -> dict[str, int]:
        """Create topics (called under lock).

        Returns:
            Dict mapping section name to thread_id
        """
        existing = await self._get_stored_topics(user_id)
        if len(existing) == len(TOPIC_CONFIG):
            return existing

        # Create missing topics
        created_any = False
        for section, config in TOPIC_CONFIG.items():
            if section in existing:
                continue

            try:
                result = await self.bot.create_forum_topic(
                    chat_id=user_id,
                    name=config["name"],
                    icon_color=config["icon_color"],
                )
                existing[section] = result.message_thread_id
                created_any = True
                logger.info(
                    f"Created topic '{config['name']}' for user {user_id}: "
                    f"thread_id={result.message_thread_id}"
                )
            except TelegramBadRequest as e:
                if "TOPICS_NOT_ENABLED" in str(e) or "not enough rights" in str(e):
                    logger.warning(
                        f"Topics not supported for user {user_id}: {e}"
                    )
                    return {}
                logger.error(f"Failed to create topic for user {user_id}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error creating topic for user {user_id}: {e}")
                break

        # Always store what we have (even partial) to avoid duplicate creation
        if created_any:
            await self._store_topics(user_id, existing)
        return existing

    async def handle_invalid_topic(self, user_id: int, section: str) -> Optional[int]:
        """Handle case when a stored topic ID is invalid (deleted/not found).

        Removes the invalid topic from Redis and creates a new one.

        Args:
            user_id: Telegram user ID
            section: Section name (e.g., 'impulses', 'bablo')

        Returns:
            New topic thread ID or None
        """
        lock = self._get_lock(user_id)
        async with lock:
            existing = await self._get_stored_topics(user_id)
            # Remove the invalid section
            if section in existing:
                del existing[section]
                await self._store_topics(user_id, existing)
                logger.info(f"Removed invalid topic '{section}' for user {user_id}")

        # Re-create topics (ensure_topics will create the missing one)
        topics = await self.ensure_topics(user_id)
        return topics.get(section)

    async def delete_topics(self, user_id: int) -> None:
        """Remove stored topic IDs for a user (does not delete Telegram topics)."""
        redis = await get_redis_client()
        await redis.delete(f"{REDIS_KEY_TOPICS}:{user_id}")

    async def _get_stored_topics(self, user_id: int) -> dict[str, int]:
        """Load topic IDs from Redis."""
        try:
            redis = await get_redis_client()
            data = await redis.get(f"{REDIS_KEY_TOPICS}:{user_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to load topics for user {user_id}: {e}")
        return {}

    async def _store_topics(self, user_id: int, topics: dict[str, int]) -> None:
        """Save topic IDs to Redis."""
        try:
            redis = await get_redis_client()
            await redis.set(
                f"{REDIS_KEY_TOPICS}:{user_id}",
                json.dumps(topics),
            )
        except Exception as e:
            logger.error(f"Failed to store topics for user {user_id}: {e}")


# Global instance
_topic_manager: Optional[TopicManager] = None


def init_topic_manager(bot: Bot) -> TopicManager:
    """Initialize global topic manager."""
    global _topic_manager
    _topic_manager = TopicManager(bot)
    return _topic_manager


def get_topic_manager() -> Optional[TopicManager]:
    """Get global topic manager instance."""
    return _topic_manager

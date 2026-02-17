"""Rate-limited Telegram message queue.

Handles Telegram Bot API rate limits (~30 messages/second).
All messages go through this queue to prevent hitting API limits.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramForbiddenError

from shared.utils.logger import get_logger

logger = get_logger("message_queue")

# Telegram limit is ~30 msg/sec, we use 25 to be safe
MESSAGES_PER_SECOND = 25
MESSAGE_INTERVAL = 1.0 / MESSAGES_PER_SECOND  # ~0.04 seconds


@dataclass
class QueuedMessage:
    """Message waiting to be sent."""

    user_id: int
    text: str
    parse_mode: Optional[str] = "HTML"
    disable_notification: bool = False
    message_thread_id: Optional[int] = None


class TelegramMessageQueue:
    """Rate-limited message queue for Telegram.

    Usage:
        queue = TelegramMessageQueue(bot)
        await queue.start()

        # Add messages - they'll be sent at controlled rate
        await queue.send(user_id, "Hello!")

        # Or bulk send
        await queue.send_bulk(user_ids, "Same message to all")
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self._queue: asyncio.Queue[QueuedMessage] = asyncio.Queue()
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._stats = {"sent": 0, "failed": 0, "blocked": 0}

    async def start(self) -> None:
        """Start the queue worker."""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info(f"Message queue started (rate: {MESSAGES_PER_SECOND} msg/sec)")

    async def stop(self) -> None:
        """Stop the queue worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info(
            f"Message queue stopped. Stats: sent={self._stats['sent']}, "
            f"failed={self._stats['failed']}, blocked={self._stats['blocked']}"
        )

    async def send(
        self,
        user_id: int,
        text: str,
        parse_mode: Optional[str] = "HTML",
        disable_notification: bool = False,
        message_thread_id: Optional[int] = None,
    ) -> None:
        """Add message to queue.

        Args:
            user_id: Telegram user ID
            text: Message text
            parse_mode: Parse mode (HTML, Markdown, None)
            disable_notification: Send silently
            message_thread_id: Topic thread ID for private chat topics
        """
        message = QueuedMessage(
            user_id=user_id,
            text=text,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
        )
        await self._queue.put(message)

    async def send_bulk(
        self,
        user_ids: list[int],
        text: str,
        parse_mode: Optional[str] = "HTML",
        disable_notification: bool = False,
        message_thread_id: Optional[int] = None,
    ) -> None:
        """Add same message for multiple users to queue.

        Args:
            user_ids: List of Telegram user IDs
            text: Message text (same for all)
            parse_mode: Parse mode
            disable_notification: Send silently
            message_thread_id: Topic thread ID for private chat topics
        """
        for user_id in user_ids:
            await self.send(
                user_id, text, parse_mode, disable_notification, message_thread_id
            )

    @property
    def pending_count(self) -> int:
        """Number of messages waiting in queue."""
        return self._queue.qsize()

    async def _worker(self) -> None:
        """Process messages from queue at controlled rate."""
        while self._running:
            try:
                # Wait for message with timeout to allow checking _running
                try:
                    message = await asyncio.wait_for(
                        self._queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Send message
                await self._send_message(message)

                # Rate limiting delay
                await asyncio.sleep(MESSAGE_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue worker error: {e}", exc_info=True)
                await asyncio.sleep(1.0)

    async def _send_message(self, message: QueuedMessage) -> bool:
        """Send a single message with error handling.

        If sending to a topic fails with MESSAGE_THREAD_INVALID,
        falls back to sending without topic (General chat).

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        try:
            kwargs = {
                "chat_id": message.user_id,
                "text": message.text,
                "parse_mode": message.parse_mode,
                "disable_notification": message.disable_notification,
            }
            if message.message_thread_id:
                kwargs["message_thread_id"] = message.message_thread_id
            await self.bot.send_message(**kwargs)
            self._stats["sent"] += 1
            return True

        except TelegramBadRequest as e:
            error_msg = str(e)
            if message.message_thread_id and (
                "MESSAGE_THREAD_INVALID" in error_msg
                or "message thread not found" in error_msg.lower()
                or "TOPIC_CLOSED" in error_msg
                or "TOPIC_DELETED" in error_msg
            ):
                # Topic ID is invalid — send to General chat as fallback
                logger.warning(
                    f"Invalid topic {message.message_thread_id} for user "
                    f"{message.user_id}, sending to General chat"
                )
                try:
                    await self.bot.send_message(
                        chat_id=message.user_id,
                        text=message.text,
                        parse_mode=message.parse_mode,
                        disable_notification=message.disable_notification,
                    )
                    self._stats["sent"] += 1
                    return True
                except Exception as fallback_err:
                    self._stats["failed"] += 1
                    logger.error(
                        f"Fallback send also failed for {message.user_id}: {fallback_err}"
                    )
                    return False
            else:
                self._stats["failed"] += 1
                logger.error(f"Failed to send to {message.user_id}: {e}")
                return False

        except TelegramRetryAfter as e:
            # Rate limited - wait and retry
            logger.warning(f"Rate limited, waiting {e.retry_after}s")
            await asyncio.sleep(e.retry_after)
            # Re-queue the message
            await self._queue.put(message)
            return False

        except TelegramForbiddenError:
            # User blocked the bot
            self._stats["blocked"] += 1
            logger.debug(f"User {message.user_id} blocked the bot")
            return False

        except Exception as e:
            self._stats["failed"] += 1
            logger.error(f"Failed to send to {message.user_id}: {e}")
            return False


# Global queue instance
_message_queue: Optional[TelegramMessageQueue] = None


def init_message_queue(bot: Bot) -> TelegramMessageQueue:
    """Initialize global message queue.

    Args:
        bot: Telegram bot instance

    Returns:
        TelegramMessageQueue instance
    """
    global _message_queue
    _message_queue = TelegramMessageQueue(bot)
    return _message_queue


def get_message_queue() -> Optional[TelegramMessageQueue]:
    """Get global message queue instance."""
    return _message_queue

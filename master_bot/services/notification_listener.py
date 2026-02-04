"""Redis notification listener for push notifications."""

import asyncio
import json
import re
from html import escape as html_escape
from typing import Optional

from aiogram import Bot

from services.message_queue import get_message_queue
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from config import settings
from shared.constants import (
    REDIS_CHANNEL_NOTIFICATIONS,
    REDIS_CHANNEL_BABLO,
    REDIS_CHANNEL_ERRORS,
    EVENT_IMPULSE_ALERT,
    EVENT_ACTIVITY_ALERT,
    EVENT_REPORT_READY,
    EVENT_BABLO_SIGNAL,
    EVENT_BABLO_ACTIVITY,
    EVENT_SERVICE_ERROR,
)

logger = get_logger("notification_listener")


class NotificationListener:
    """Listener for Redis pub/sub notifications."""

    def __init__(self, bot: Bot):
        """Initialize listener.

        Args:
            bot: Telegram bot instance
        """
        self.bot = bot
        self._running = False
        self._pending_reports: dict[tuple[int, str], dict] = {}
        self._report_timeout = 5.0

    async def start(self) -> None:
        """Start listening for notifications."""
        self._running = True
        logger.info("Starting notification listener...")

        try:
            logger.info("Getting Redis client...")
            redis = await get_redis_client()
            logger.info("Redis client obtained")
            pubsub = await redis.subscribe(
                REDIS_CHANNEL_NOTIFICATIONS,
                REDIS_CHANNEL_BABLO,
                REDIS_CHANNEL_ERRORS,
            )
            logger.info(f"✅ Subscribed to channels: {REDIS_CHANNEL_NOTIFICATIONS}, {REDIS_CHANNEL_BABLO}, {REDIS_CHANNEL_ERRORS}")

            async for message in pubsub.listen():
                if not self._running:
                    break

                if message["type"] != "message":
                    continue

                try:
                    data = json.loads(message["data"])
                    channel = message.get("channel", "")
                    if isinstance(channel, bytes):
                        channel = channel.decode()
                    event = data.get("event", "unknown")
                    user_id = data.get("user_id", "?")
                    logger.info(f"📨 Received {event} for user {user_id} on {channel}")
                    await self._handle_notification(data, channel)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in notification: {message['data'][:200]} - Error: {e}")
                except Exception as e:
                    logger.error(f"Error handling notification: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Notification listener error: {e}")
            if self._running:
                # Reconnect after delay
                await asyncio.sleep(5)
                asyncio.create_task(self.start())

    async def stop(self) -> None:
        """Stop listening for notifications."""
        self._running = False
        logger.info("Notification listener stopped.")

    async def _handle_notification(self, data: dict, channel: str = "") -> None:
        """Handle incoming notification.

        Args:
            data: Notification data
            channel: Redis channel name
        """
        event = data.get("event")
        user_id = data.get("user_id")
        event_data = data.get("data", {})

        if not event or not user_id:
            logger.warning(f"Missing event or user_id in notification: event={event}, user_id={user_id}")
            return

        if event == EVENT_IMPULSE_ALERT:
            await self._send_impulse_alert(user_id, event_data)
        elif event == EVENT_ACTIVITY_ALERT:
            await self._send_activity_alert(user_id, event_data)
        elif event == EVENT_BABLO_SIGNAL:
            await self._send_bablo_signal(user_id, event_data)
        elif event == EVENT_BABLO_ACTIVITY:
            await self._send_bablo_activity_alert(user_id, event_data)
        elif event == EVENT_REPORT_READY:
            source = "impulse" if channel == REDIS_CHANNEL_NOTIFICATIONS else "bablo"
            await self._handle_report_part(user_id, event_data, source)
        elif event == EVENT_SERVICE_ERROR:
            await self._send_service_error_to_admin(data)

    async def _send_impulse_alert(self, user_id: int, data: dict) -> None:
        """Send impulse alert to user.

        Args:
            user_id: Telegram user ID
            data: Impulse data
        """
        symbol = data.get("symbol", "N/A")
        percent = data.get("percent", 0)
        impulse_type = data.get("type", "growth")

        if impulse_type == "growth":
            emoji = "🟢"
            direction = "рост"
        else:
            emoji = "🔴"
            direction = "падение"

        text = (
            f"{emoji} <b>Импульс: {symbol}</b>\n\n"
            f"Тип: {direction}\n"
            f"Изменение: <b>{percent:+.2f}%</b>"
        )

        queue = get_message_queue()
        if queue:
            await queue.send(user_id, text)
            logger.info(f"✅ Impulse alert queued for {user_id}: {symbol} {percent:+.2f}%")
        else:
            # Fallback to direct send if queue not initialized
            try:
                await self.bot.send_message(user_id, text)
                logger.info(f"✅ Impulse alert sent to {user_id}: {symbol} {percent:+.2f}%")
            except Exception as e:
                logger.error(f"Failed to send impulse alert to {user_id}: {e}")

    async def _send_activity_alert(self, user_id: int, data: dict) -> None:
        """Send activity alert to user.

        Args:
            user_id: Telegram user ID
            data: Activity data
        """
        count = data.get("count", 0)
        window = data.get("window_minutes", 15)

        text = (
            f"⚡ <b>Высокая активность рынка!</b>\n\n"
            f"За последние {window} минут зафиксировано "
            f"<b>{count}</b> импульсов.\n\n"
            f"Рекомендуется проверить ситуацию на рынке."
        )

        queue = get_message_queue()
        if queue:
            await queue.send(user_id, text)
            logger.info(f"✅ Activity alert queued for {user_id}: {count} impulses in {window}m")
        else:
            try:
                await self.bot.send_message(user_id, text)
                logger.info(f"✅ Activity alert sent to {user_id}: {count} impulses in {window}m")
            except Exception as e:
                logger.error(f"Failed to send activity alert to {user_id}: {e}")

    @staticmethod
    def _convert_tv_markdown_to_html(text: str) -> str:
        """Convert TradingView markdown formatting to Telegram HTML.

        TradingView uses standard markdown (**bold**, __emphasis__, [text](url))
        which differs from Telegram's Markdown v1 (*bold*, _italic_).
        """
        # Extract and preserve markdown links before HTML escaping
        links: list[tuple[str, str]] = []

        def _save_link(m: re.Match) -> str:
            idx = len(links)
            links.append((m.group(1), m.group(2)))
            return f"\x00LINK{idx}\x00"

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _save_link, text)

        # HTML-escape the rest
        text = html_escape(text)

        # Convert **bold** → <b>bold</b>
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.DOTALL)

        # Convert __emphasis__ → <b>emphasis</b>
        text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)

        # Restore links as HTML <a> tags
        for i, (link_text, url) in enumerate(links):
            text = text.replace(
                f"\x00LINK{i}\x00",
                f'<a href="{html_escape(url)}">{html_escape(link_text)}</a>',
            )

        return text

    async def _send_bablo_signal(self, user_id: int, data: dict) -> None:
        """Send Bablo signal alert to user.

        Args:
            user_id: Telegram user ID
            data: Signal data
        """
        # Use original text from TradingView (converted to HTML)
        original_text = data.get("original_text")
        symbol = data.get("symbol", "N/A")

        if not original_text:
            # Fallback to basic format if original text is not available
            direction = data.get("direction", "long")
            strength = data.get("strength", 3)
            timeframe = data.get("timeframe", "")
            quality = data.get("quality_total", 0)

            strength_squares = ("🟩" if direction == "long" else "🟥") * strength + "⬜" * (5 - strength)
            text = f"{strength_squares} {html_escape(symbol)}\n⏱: {timeframe} | ⭐: {quality}/10"
        else:
            # Convert TradingView markdown (**bold**, __em__, [link](url)) to HTML
            text = self._convert_tv_markdown_to_html(original_text)

        queue = get_message_queue()
        if queue:
            await queue.send(user_id, text)
            logger.info(f"✅ Bablo signal queued for {user_id}: {symbol}")
        else:
            try:
                await self.bot.send_message(user_id, text)
                logger.info(f"✅ Bablo signal sent to {user_id}: {symbol}")
            except Exception as e:
                logger.error(f"Failed to send Bablo signal to {user_id}: {e}")

    async def _send_bablo_activity_alert(self, user_id: int, data: dict) -> None:
        """Send Bablo activity alert to user.

        Args:
            user_id: Telegram user ID
            data: Activity data
        """
        signal_count = data.get("signal_count", 0)
        window_minutes = data.get("window_minutes", 15)
        threshold = data.get("threshold", 10)

        text = (
            f"📈 <b>Высокая активность Bablo!</b>\n\n"
            f"За последние {window_minutes} мин: <b>{signal_count}</b> сигналов\n"
            f"Порог срабатывания: {threshold} сигналов"
        )

        queue = get_message_queue()
        if queue:
            await queue.send(user_id, text)
            logger.info(f"✅ Bablo activity alert queued for {user_id}: {signal_count} signals in {window_minutes}m")
        else:
            try:
                await self.bot.send_message(user_id, text)
                logger.info(f"✅ Bablo activity alert sent to {user_id}: {signal_count} signals in {window_minutes}m")
            except Exception as e:
                logger.error(f"Failed to send Bablo activity alert to {user_id}: {e}")

    async def _handle_report_part(
        self, user_id: int, data: dict, source: str
    ) -> None:
        """Handle report part for combined reports.

        Args:
            user_id: Telegram user ID
            data: Report data
            source: Source service (impulse or bablo)
        """
        report_type = data.get("report_type", "evening")
        key = (user_id, report_type)

        if key not in self._pending_reports:
            self._pending_reports[key] = {
                "impulse": None,
                "bablo": None,
                "expects_both": data.get("expects_combined", False),
            }
            asyncio.create_task(self._report_timeout_handler(key))

        self._pending_reports[key][source] = data

        if not self._pending_reports[key]["expects_both"]:
            await self._send_combined_report(key)
        elif (
            self._pending_reports[key]["impulse"] is not None
            and self._pending_reports[key]["bablo"] is not None
        ):
            await self._send_combined_report(key)

    async def _report_timeout_handler(self, key: tuple[int, str]) -> None:
        """Handle timeout for combined reports.

        Args:
            key: (user_id, report_type) tuple
        """
        await asyncio.sleep(self._report_timeout)

        if key in self._pending_reports:
            await self._send_combined_report(key)

    async def _send_combined_report(self, key: tuple[int, str]) -> None:
        """Send combined or single report.

        Args:
            key: (user_id, report_type) tuple
        """
        if key not in self._pending_reports:
            return

        user_id, report_type = key
        parts = self._pending_reports.pop(key)

        impulse_data = parts.get("impulse")
        bablo_data = parts.get("bablo")

        report_titles = {
            "morning": "🌅 Утренний отчёт",
            "evening": "🌆 Вечерний отчёт",
            "weekly": "📊 Недельный отчёт",
            "monthly": "📊 Месячный отчёт",
        }
        title = report_titles.get(report_type, "📊 Отчёт")

        sections = [f"<b>{title}</b>"]

        if impulse_data and bablo_data:
            sections.append("")
            sections.append("━━━━━━━━━━━━━━━━━━━━━")
            sections.append("📊 <b>ИМПУЛЬСЫ</b>")
            sections.append("━━━━━━━━━━━━━━━━━━━━━")
            sections.append(impulse_data.get("content", ""))
            sections.append("")
            sections.append("━━━━━━━━━━━━━━━━━━━━━")
            sections.append("💰 <b>BABLO СИГНАЛЫ</b>")
            sections.append("━━━━━━━━━━━━━━━━━━━━━")
            sections.append(bablo_data.get("content", ""))
        elif impulse_data:
            sections.append("")
            sections.append(impulse_data.get("text", impulse_data.get("content", "")))
        elif bablo_data:
            sections.append("")
            sections.append(bablo_data.get("text", bablo_data.get("content", "")))
        else:
            return

        text = "\n".join(sections)

        queue = get_message_queue()
        if queue:
            await queue.send(user_id, text)
            logger.info(f"✅ Report ({report_type}) queued for {user_id}")
        else:
            try:
                await self.bot.send_message(user_id, text)
                logger.info(f"✅ Report ({report_type}) sent to {user_id}")
            except Exception as e:
                logger.error(f"Failed to send report to {user_id}: {e}")

    async def _send_service_error_to_admin(self, data: dict) -> None:
        """Send service error notification to admin.

        Args:
            data: Error data from microservice
        """
        service = data.get("service", "unknown")
        error_type = data.get("error_type", "UnknownError")
        error_message = data.get("error_message", "No message")
        context = data.get("context")
        user_id = data.get("user_id")
        timestamp = data.get("timestamp", "")

        parts = [f"⚠️ <b>Ошибка в {service}</b>\n"]

        if user_id:
            parts.append(f"👤 User ID: <code>{user_id}</code>")

        if context:
            parts.append(f"📍 Место: <code>{context}</code>")

        parts.append(f"❌ Тип: <code>{error_type}</code>")
        parts.append(f"📝 Описание: <code>{error_message[:300]}</code>")

        if timestamp:
            parts.append(f"\n🕐 Время: {timestamp}")

        message = "\n".join(parts)

        try:
            await self.bot.send_message(settings.ADMIN_ID, message)
            logger.info(f"✅ Service error sent to admin: {service}/{error_type}")
        except Exception as e:
            logger.error(f"Failed to send service error to admin: {e}")

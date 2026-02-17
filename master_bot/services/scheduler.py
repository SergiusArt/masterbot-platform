"""Unified scheduler for sending reports from all services.

Optimizations:
- Report caching: generates report content once, sends to all users
- Rate-limited queue: respects Telegram API limits (30 msg/sec)
"""

from typing import Optional

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from services.impulse_client import impulse_client
from services.bablo_client import bablo_client
from services.message_queue import get_message_queue
from services.topic_manager import get_topic_manager
from config import settings
from shared.utils.logger import get_logger
from shared.constants import TOPIC_REPORTS

logger = get_logger("scheduler")


class ReportScheduler:
    """Scheduler for sending combined reports from all services."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.tz = pytz.timezone(settings.TIMEZONE)
        self.scheduler = AsyncIOScheduler(timezone=self.tz)

    def start(self) -> None:
        """Start the scheduler."""
        # Morning reports at 8:00
        self.scheduler.add_job(
            self._send_morning_reports,
            CronTrigger(hour=8, minute=0, timezone=self.tz),
            id="morning_reports",
            replace_existing=True,
        )

        # Evening reports at 20:00
        self.scheduler.add_job(
            self._send_evening_reports,
            CronTrigger(hour=20, minute=0, timezone=self.tz),
            id="evening_reports",
            replace_existing=True,
        )

        # Weekly reports on Monday at 9:00
        self.scheduler.add_job(
            self._send_weekly_reports,
            CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=self.tz),
            id="weekly_reports",
            replace_existing=True,
        )

        # Monthly reports on 1st day at 9:00
        self.scheduler.add_job(
            self._send_monthly_reports,
            CronTrigger(day=1, hour=9, minute=0, timezone=self.tz),
            id="monthly_reports",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(
            f"Scheduler started ({self.tz}): morning (8:00), evening (20:00), "
            "weekly (Mon 9:00), monthly (1st 9:00)"
        )

    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")

    async def _send_morning_reports(self) -> None:
        """Send morning reports to all subscribed users."""
        await self._send_reports("morning", "🌅 Утренний отчёт")

    async def _send_evening_reports(self) -> None:
        """Send evening reports to all subscribed users."""
        await self._send_reports("evening", "🌆 Вечерний отчёт")

    async def _send_weekly_reports(self) -> None:
        """Send weekly reports to all subscribed users."""
        await self._send_reports("weekly", "📊 Недельный отчёт")

    async def _send_monthly_reports(self) -> None:
        """Send monthly reports to all subscribed users."""
        await self._send_reports("monthly", "📊 Месячный отчёт")

    async def _send_reports(self, report_type: str, title: str) -> None:
        """Send reports to all subscribed users.

        Optimized version:
        - Generates report content once per service (cached)
        - Groups users by their service subscriptions
        - Uses rate-limited queue for sending

        Args:
            report_type: Report type (morning, evening, weekly, monthly)
            title: Report title
        """
        logger.info(f"Sending {report_type} reports...")

        # Get all users who have reports enabled from both services
        users_to_notify = await self._get_users_for_report(report_type)

        if not users_to_notify:
            logger.info(f"No users subscribed to {report_type} reports")
            return

        # Cache report content - generate once, send to many
        impulse_content = await self._get_cached_report("impulse", report_type)
        bablo_content = await self._get_cached_report("bablo", report_type)

        # Group users by their subscription type
        impulse_only_users: list[int] = []
        bablo_only_users: list[int] = []
        both_users: list[int] = []

        for user_id, services in users_to_notify.items():
            has_impulse = services.get("impulse") and impulse_content
            has_bablo = services.get("bablo") and bablo_content

            if has_impulse and has_bablo:
                both_users.append(user_id)
            elif has_impulse:
                impulse_only_users.append(user_id)
            elif has_bablo:
                bablo_only_users.append(user_id)

        # Generate report texts (once per group)
        closings = {
            "morning": "\nХорошего дня!",
            "evening": "\nХорошего вечера!",
            "weekly": "",
            "monthly": "",
        }
        closing = closings.get(report_type, "")

        queue = get_message_queue()
        tm = get_topic_manager()
        queued_count = 0

        # Build text per group
        texts: list[tuple[list[int], str]] = []

        if both_users and impulse_content and bablo_content:
            text = (
                f"<b>{title}</b>\n\n"
                f"── <b>Импульсы</b> ──\n{impulse_content}\n\n"
                f"── <b>Bablo</b> ──\n{bablo_content}"
                f"{closing}"
            )
            texts.append((both_users, text))

        if impulse_only_users and impulse_content:
            texts.append((impulse_only_users, f"<b>{title}</b>\n\n{impulse_content}{closing}"))

        if bablo_only_users and bablo_content:
            texts.append((bablo_only_users, f"<b>{title}</b>\n\n{bablo_content}{closing}"))

        # Send to each user with topic routing
        for user_ids, text in texts:
            for user_id in user_ids:
                topic_id = None
                if tm:
                    try:
                        topic_id = await tm.get_topic_id(user_id, TOPIC_REPORTS)
                    except Exception:
                        pass

                if queue:
                    await queue.send(user_id, text, message_thread_id=topic_id)
                else:
                    try:
                        kwargs = {"chat_id": user_id, "text": text}
                        if topic_id:
                            kwargs["message_thread_id"] = topic_id
                        await self.bot.send_message(**kwargs)
                    except Exception as e:
                        logger.error(f"Failed to send report to {user_id}: {e}")
                        continue
                queued_count += 1

        logger.info(f"{report_type.capitalize()} reports queued for {queued_count} users")

    async def _get_cached_report(self, service: str, report_type: str) -> Optional[str]:
        """Get report content from service (cached per report cycle).

        Reports are the same for all users (market data, not personalized),
        so we generate once and send to all subscribers.

        Args:
            service: Service name (impulse or bablo)
            report_type: Report type

        Returns:
            Report text content or None
        """
        try:
            if service == "impulse":
                # user_id is required by API but not used in report generation
                report = await impulse_client.generate_report(report_type, user_id=0)
            else:
                report = await bablo_client.generate_report(report_type)

            report_data = report.get("report", {})
            return report_data.get("text") if report_data else None
        except Exception as e:
            logger.error(f"Error getting {service} report: {e}")
            return None

    async def _get_users_for_report(
        self, report_type: str
    ) -> dict[int, dict[str, bool]]:
        """Get users subscribed to report type with their service preferences.

        Args:
            report_type: Report type

        Returns:
            Dictionary mapping user_id to {impulse: bool, bablo: bool}
        """
        users: dict[int, dict[str, bool]] = {}

        # Get users from impulse service via API
        try:
            impulse_users = await impulse_client.get_users_for_report(report_type)
            for user_id in impulse_users:
                if user_id not in users:
                    users[user_id] = {"impulse": False, "bablo": False}
                users[user_id]["impulse"] = True
        except Exception as e:
            logger.error(f"Error getting impulse users for {report_type} report: {e}")

        # Get users from bablo service via API
        try:
            bablo_users = await bablo_client.get_users_for_report(report_type)
            for user_id in bablo_users:
                if user_id not in users:
                    users[user_id] = {"impulse": False, "bablo": False}
                users[user_id]["bablo"] = True
        except Exception as e:
            logger.error(f"Error getting bablo users for {report_type} report: {e}")

        return users

    async def _generate_combined_report(
        self,
        user_id: int,
        report_type: str,
        title: str,
        services: dict[str, bool],
    ) -> Optional[str]:
        """Generate combined report from enabled services.

        Args:
            user_id: User ID
            report_type: Report type
            title: Report title
            services: Dictionary of enabled services

        Returns:
            Formatted report text or None
        """
        sections = [f"<b>{title}</b>"]
        has_content = False
        both_services = services.get("impulse") and services.get("bablo")

        # Get impulse report
        if services.get("impulse"):
            try:
                report = await impulse_client.generate_report(report_type, user_id)
                report_data = report.get("report", {})
                if report_data and report_data.get("text"):
                    if both_services:
                        sections.append("")
                        sections.append("── <b>Импульсы</b> ──")
                    else:
                        sections.append("")
                    sections.append(report_data.get("text", ""))
                    has_content = True
            except Exception as e:
                logger.error(f"Error getting impulse report for {user_id}: {e}")

        # Get bablo report
        if services.get("bablo"):
            try:
                report = await bablo_client.generate_report(report_type)
                report_data = report.get("report", {})
                if report_data and report_data.get("text"):
                    if both_services and has_content:
                        sections.append("")
                        sections.append("── <b>Bablo</b> ──")
                    elif not has_content:
                        sections.append("")
                    sections.append(report_data.get("text", ""))
                    has_content = True
            except Exception as e:
                logger.error(f"Error getting bablo report for {user_id}: {e}")

        if not has_content:
            return None

        # Add closing greeting
        closings = {
            "morning": "\nХорошего дня!",
            "evening": "\nХорошего вечера!",
            "weekly": "",
            "monthly": "",
        }
        closing = closings.get(report_type, "")
        if closing:
            sections.append(closing)

        return "\n".join(sections)


# Global scheduler instance (will be initialized with bot in main.py)
report_scheduler: Optional[ReportScheduler] = None


def init_scheduler(bot: Bot) -> ReportScheduler:
    """Initialize the global scheduler.

    Args:
        bot: Telegram bot instance

    Returns:
        ReportScheduler instance
    """
    global report_scheduler
    report_scheduler = ReportScheduler(bot)
    return report_scheduler


async def trigger_report_manually(report_type: str) -> str:
    """Manually trigger a report for testing.

    Args:
        report_type: Report type (morning, evening, weekly, monthly)

    Returns:
        Status message
    """
    if report_scheduler is None:
        return "Scheduler not initialized"

    try:
        if report_type == "morning":
            await report_scheduler._send_morning_reports()
        elif report_type == "evening":
            await report_scheduler._send_evening_reports()
        elif report_type == "weekly":
            await report_scheduler._send_weekly_reports()
        elif report_type == "monthly":
            await report_scheduler._send_monthly_reports()
        else:
            return f"Unknown report type: {report_type}"
        return f"Report '{report_type}' sent successfully"
    except Exception as e:
        logger.error(f"Error triggering {report_type} report: {e}", exc_info=True)
        return f"Error: {e}"

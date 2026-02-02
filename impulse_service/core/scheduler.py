"""Scheduler for periodic tasks."""

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.report_service import report_service
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.constants import REDIS_CHANNEL_NOTIFICATIONS, EVENT_REPORT_READY
from config import settings

logger = get_logger("scheduler")

_tz = pytz.timezone(settings.TIMEZONE)
scheduler = AsyncIOScheduler(timezone=_tz)


async def send_morning_reports():
    """Send morning reports to subscribed users."""
    logger.info("Sending morning reports...")

    from sqlalchemy import select
    from models.impulse import UserNotificationSettings
    from shared.database.connection import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(UserNotificationSettings.user_id).where(
                UserNotificationSettings.morning_report == True
            )
        )
        user_ids = [row[0] for row in result.all()]

    if not user_ids:
        logger.info("No users subscribed to morning reports")
        return

    redis = await get_redis_client()

    for user_id in user_ids:
        try:
            report = await report_service.generate_report("morning", user_id)
            await redis.publish(
                REDIS_CHANNEL_NOTIFICATIONS,
                {
                    "event": EVENT_REPORT_READY,
                    "user_id": user_id,
                    "data": {
                        "report_type": "morning",
                        "text": report.text,
                        "content": report.text,
                        "timestamp": report.generated_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Morning report sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send morning report to {user_id}: {e}")

    logger.info(f"Morning reports sent to {len(user_ids)} users")


async def send_evening_reports():
    """Send evening reports to subscribed users."""
    logger.info("Sending evening reports...")

    from sqlalchemy import select
    from models.impulse import UserNotificationSettings
    from shared.database.connection import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(UserNotificationSettings.user_id).where(
                UserNotificationSettings.evening_report == True
            )
        )
        user_ids = [row[0] for row in result.all()]

    if not user_ids:
        logger.info("No users subscribed to evening reports")
        return

    redis = await get_redis_client()

    for user_id in user_ids:
        try:
            report = await report_service.generate_report("evening", user_id)
            await redis.publish(
                REDIS_CHANNEL_NOTIFICATIONS,
                {
                    "event": EVENT_REPORT_READY,
                    "user_id": user_id,
                    "data": {
                        "report_type": "evening",
                        "text": report.text,
                        "content": report.text,
                        "timestamp": report.generated_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Evening report sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send evening report to {user_id}: {e}")

    logger.info(f"Evening reports sent to {len(user_ids)} users")


async def send_weekly_reports():
    """Send weekly reports to subscribed users."""
    logger.info("Sending weekly reports...")

    from sqlalchemy import select
    from models.impulse import UserNotificationSettings
    from shared.database.connection import async_session_maker

    async with async_session_maker() as session:
        result = await session.execute(
            select(UserNotificationSettings.user_id).where(
                UserNotificationSettings.weekly_report == True
            )
        )
        user_ids = [row[0] for row in result.all()]

    if not user_ids:
        logger.info("No users subscribed to weekly reports")
        return

    redis = await get_redis_client()

    for user_id in user_ids:
        try:
            report = await report_service.generate_report("weekly", user_id)
            await redis.publish(
                REDIS_CHANNEL_NOTIFICATIONS,
                {
                    "event": EVENT_REPORT_READY,
                    "user_id": user_id,
                    "data": {
                        "report_type": "weekly",
                        "text": report.text,
                        "content": report.text,
                        "timestamp": report.generated_at.isoformat(),
                    },
                },
            )
            logger.debug(f"Weekly report sent to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send weekly report to {user_id}: {e}")

    logger.info(f"Weekly reports sent to {len(user_ids)} users")


def start_scheduler():
    """Start the scheduler."""
    # Morning reports at 8:00
    scheduler.add_job(
        send_morning_reports,
        CronTrigger(hour=8, minute=0, timezone=_tz),
        id="morning_reports",
        replace_existing=True,
    )

    # Evening reports at 20:00
    scheduler.add_job(
        send_evening_reports,
        CronTrigger(hour=20, minute=0, timezone=_tz),
        id="evening_reports",
        replace_existing=True,
    )

    # Weekly reports on Monday at 9:00
    scheduler.add_job(
        send_weekly_reports,
        CronTrigger(day_of_week="mon", hour=9, minute=0, timezone=_tz),
        id="weekly_reports",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"Scheduler started ({_tz}): morning (8:00), evening (20:00), weekly (Mon 9:00)")


def stop_scheduler():
    """Stop the scheduler."""
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")

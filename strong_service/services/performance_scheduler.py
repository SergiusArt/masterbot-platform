"""Periodic scheduler for auto-calculating matured signal performance."""

import asyncio
import json

from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from models.strong import StrongSignal
from services.performance_service import performance_service, MATURITY_HOURS
from services.notification_service import notification_service
from shared.database.connection import async_session_maker
from shared.utils.redis_client import get_redis_client
from shared.utils.logger import get_logger
from shared.constants import EVENT_STRONG_PERFORMANCE, REDIS_CHANNEL_STRONG

logger = get_logger("performance_scheduler")


class PerformanceScheduler:
    """Periodic job: calculate performance for matured signals."""

    def __init__(self, interval_minutes: int = 30):
        self._interval = interval_minutes * 60
        self._running = False
        self._task = None

    async def start(self) -> None:
        """Start the scheduler loop."""
        self._running = True
        logger.info(f"Performance scheduler started (every {self._interval // 60} min)")
        while self._running:
            try:
                await self._check_and_calculate()
            except Exception as e:
                logger.error(f"Scheduler error: {e}", exc_info=True)
            await asyncio.sleep(self._interval)

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        logger.info("Performance scheduler stopped")

    async def _check_and_calculate(self) -> None:
        """Find matured uncalculated signals and process them."""
        maturity_cutoff = datetime.now(timezone.utc) - timedelta(hours=MATURITY_HOURS)

        async with async_session_maker() as session:
            query = (
                select(StrongSignal)
                .where(
                    StrongSignal.performance_calculated_at.is_(None),
                    StrongSignal.received_at <= maturity_cutoff,
                )
                .order_by(StrongSignal.received_at.asc())
            )
            result = await session.execute(query)
            signals = list(result.scalars().all())

        if not signals:
            return

        logger.info(f"Found {len(signals)} matured signals to calculate")

        for signal in signals:
            async with async_session_maker() as session:
                try:
                    res = await performance_service.calculate_signal_performance(
                        session, signal,
                    )
                    if "error" not in res:
                        await self._publish_notification(signal, res)
                        logger.info(
                            f"Calculated {signal.symbol} {signal.direction}: "
                            f"+{res['max_profit_pct']:.2f}%"
                        )
                    else:
                        logger.warning(f"Failed to calculate {signal.symbol}: {res['error']}")
                except Exception as e:
                    logger.error(f"Error calculating {signal.symbol}: {e}")

            from services.binance_client import binance_client
            await binance_client.throttle()

    async def _publish_notification(self, signal: StrongSignal, result: dict) -> None:
        """Publish performance notification to all subscribed users."""
        try:
            async with async_session_maker() as session:
                users = await notification_service.get_users_for_notification(
                    session, direction=signal.direction,
                )

            if not users:
                return

            redis = await get_redis_client()
            messages = [
                {
                    "event": EVENT_STRONG_PERFORMANCE,
                    "user_id": user_id,
                    "data": {
                        "symbol": signal.symbol,
                        "direction": signal.direction,
                        "max_profit_pct": result["max_profit_pct"],
                        "entry_price": result["entry_price"],
                        "bars_to_max": result["bars_to_max"],
                    },
                }
                for user_id in users
            ]

            await redis.publish_batch(REDIS_CHANNEL_STRONG, messages)
            logger.info(f"Published performance notification for {signal.symbol} to {len(users)} users")

        except Exception as e:
            logger.error(f"Error publishing performance notification: {e}")


# Global instance
performance_scheduler = PerformanceScheduler()

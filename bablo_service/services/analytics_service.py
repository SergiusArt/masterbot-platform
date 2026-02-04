"""Analytics service for Bablo signals."""

import statistics
from datetime import datetime, timedelta
from typing import Optional
import pytz

from sqlalchemy import select, func, cast, Date, extract, text
from sqlalchemy.ext.asyncio import AsyncSession

from services.signal_service import signal_service
from models.bablo import BabloSignal
from config import settings
from shared.utils.logger import get_logger

logger = get_logger("bablo_analytics_service")


class AnalyticsService:
    """Service for computing Bablo signal analytics."""

    def __init__(self):
        self.tz = pytz.timezone(settings.TIMEZONE)

    def _get_period_dates(self, period: str) -> tuple[datetime, datetime]:
        """Get start and end dates for period.

        Args:
            period: Period name ('today', 'yesterday', 'week', 'month')

        Returns:
            Tuple of (start_date, end_date)
        """
        now = datetime.now(self.tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if period == "today":
            return today_start, now
        elif period == "yesterday":
            yesterday_start = today_start - timedelta(days=1)
            return yesterday_start, today_start
        elif period == "week":
            week_start = today_start - timedelta(days=7)
            return week_start, now
        elif period == "month":
            month_start = today_start - timedelta(days=30)
            return month_start, now
        else:
            return today_start, now

    async def get_analytics(
        self,
        session: AsyncSession,
        period: str,
    ) -> dict:
        """Get analytics for specified period.

        Args:
            session: Database session
            period: Period name

        Returns:
            Analytics dictionary
        """
        start_date, end_date = self._get_period_dates(period)

        # Get basic stats
        total_count = await signal_service.get_signals_count(
            session, start_date, end_date
        )

        # Get direction breakdown
        direction_stats = await signal_service.get_signals_by_direction(
            session, start_date, end_date
        )

        # Get timeframe breakdown
        timeframe_stats = await signal_service.get_signals_by_timeframe(
            session, start_date, end_date
        )

        # Get top symbols
        top_symbols = await signal_service.get_top_symbols(
            session, start_date, end_date, limit=5
        )

        # Get average quality
        avg_quality = await signal_service.get_average_quality(
            session, start_date, end_date
        )

        # Calculate median (daily counts for last 14 days)
        now = datetime.now(self.tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        median_start = today_start - timedelta(days=14)

        median_counts = await self._get_daily_counts(session, median_start, today_start)
        week_median = int(statistics.median(median_counts)) if median_counts else 0

        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_signals": total_count,
            "long_count": direction_stats.get("long", 0),
            "short_count": direction_stats.get("short", 0),
            "by_timeframe": timeframe_stats,
            "top_symbols": [
                {"symbol": symbol, "count": count}
                for symbol, count in top_symbols
            ],
            "average_quality": round(avg_quality, 1) if avg_quality else None,
            "week_median": week_median,
        }

    async def get_comparison(
        self,
        session: AsyncSession,
    ) -> dict:
        """Get comparison data (vs yesterday, vs week median).

        Args:
            session: Database session

        Returns:
            Comparison dictionary
        """
        now = datetime.now(self.tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Today's count
        today_count = await signal_service.get_signals_count(
            session, today_start, now
        )

        # Yesterday's count (full day)
        yesterday_start = today_start - timedelta(days=1)
        yesterday_count = await signal_service.get_signals_count(
            session, yesterday_start, today_start
        )

        # Week average
        week_start = today_start - timedelta(days=7)
        week_total = await signal_service.get_signals_count(
            session, week_start, today_start
        )
        week_avg = week_total / 7 if week_total > 0 else 0

        # Calculate comparisons
        vs_yesterday = self._calc_comparison(today_count, yesterday_count)
        vs_week = self._calc_comparison(today_count, week_avg)

        return {
            "today": today_count,
            "yesterday": yesterday_count,
            "week_avg": round(week_avg, 1),
            "vs_yesterday": vs_yesterday,
            "vs_week_avg": vs_week,
        }

    def _calc_comparison(self, current: float, previous: float) -> str:
        """Calculate comparison string."""
        if previous == 0:
            return "—"

        diff = ((current - previous) / previous) * 100
        if diff > 0:
            return f"+{diff:.0f}%"
        elif diff < 0:
            return f"{diff:.0f}%"
        else:
            return "0%"

    async def _get_daily_counts(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ) -> list[int]:
        """Get signal counts per day for a date range."""
        local_time = func.timezone(settings.TIMEZONE, BabloSignal.received_at)
        local_date = func.date(local_time)

        query = (
            select(
                local_date.label("day"),
                func.count().label("cnt"),
            )
            .where(
                BabloSignal.received_at >= start_date,
                BabloSignal.received_at < end_date,
            )
            .group_by(local_date)
        )
        result = await session.execute(query)
        return [row.cnt for row in result.all()]

    async def get_time_series(self, session: AsyncSession, period: str) -> dict:
        """Get signal counts as time series.

        Args:
            session: Database session
            period: Period identifier (today, week, month)

        Returns:
            Time series data with labels and counts
        """
        now = datetime.now(self.tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Convert timestamp to local timezone for correct hour/day extraction
        local_time = func.timezone(settings.TIMEZONE, BabloSignal.received_at)

        if period == "today":
            # Hourly counts for today (using local timezone)
            query = (
                select(
                    extract("hour", local_time).label("hour"),
                    func.count().label("count"),
                )
                .where(BabloSignal.received_at >= today_start)
                .group_by(extract("hour", local_time))
                .order_by(extract("hour", local_time))
            )
            result = await session.execute(query)
            rows = result.all()

            # Fill in missing hours
            data = {int(row.hour): row.count for row in rows}
            current_hour = now.hour
            labels = [f"{h:02d}:00" for h in range(current_hour + 1)]
            counts = [data.get(h, 0) for h in range(current_hour + 1)]

        elif period == "week":
            # Daily counts for last 7 days (using local timezone for date)
            week_start = today_start - timedelta(days=6)
            local_date = func.date(local_time)
            query = (
                select(
                    local_date.label("day"),
                    func.count().label("count"),
                )
                .where(BabloSignal.received_at >= week_start)
                .group_by(local_date)
                .order_by(local_date)
            )
            result = await session.execute(query)
            rows = result.all()

            # Fill in missing days
            data = {row.day: row.count for row in rows}
            labels = []
            counts = []
            for i in range(7):
                day = (week_start + timedelta(days=i)).date()
                labels.append(day.strftime("%d.%m"))
                counts.append(data.get(day, 0))

        elif period == "month":
            # Daily counts for last 30 days (using local timezone for date)
            month_start = today_start - timedelta(days=29)
            local_date = func.date(local_time)
            query = (
                select(
                    local_date.label("day"),
                    func.count().label("count"),
                )
                .where(BabloSignal.received_at >= month_start)
                .group_by(local_date)
                .order_by(local_date)
            )
            result = await session.execute(query)
            rows = result.all()

            # Fill in missing days
            data = {row.day: row.count for row in rows}
            labels = []
            counts = []
            for i in range(30):
                day = (month_start + timedelta(days=i)).date()
                labels.append(day.strftime("%d.%m"))
                counts.append(data.get(day, 0))

        else:
            labels = []
            counts = []

        # Calculate median for reference line
        median = int(statistics.median(counts)) if counts else 0

        return {
            "period": period,
            "labels": labels,
            "counts": counts,
            "median": median,
            "total": sum(counts),
        }


# Global service instance
analytics_service = AnalyticsService()

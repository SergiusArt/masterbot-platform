"""Analytics service for impulse data analysis."""

import statistics
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
import pytz

from sqlalchemy import select, func, and_, cast, Date, extract

from models.impulse import Impulse
from shared.database.connection import async_session_maker
from shared.schemas.impulse import AnalyticsResponse, TopImpulse, ComparisonData
from shared.constants import AnalyticsPeriod
from config import settings


class AnalyticsService:
    """Service for computing analytics."""

    async def get_analytics(self, period: str) -> AnalyticsResponse:
        """Get analytics for specified period.

        Args:
            period: Period identifier (today, yesterday, week, month)

        Returns:
            Analytics data
        """
        start_date, end_date = self._get_period_dates(period)

        async with async_session_maker() as session:
            # Get total counts
            total_query = select(func.count()).where(
                and_(
                    Impulse.received_at >= start_date,
                    Impulse.received_at <= end_date,
                )
            )
            total = await session.scalar(total_query) or 0

            growth_query = select(func.count()).where(
                and_(
                    Impulse.received_at >= start_date,
                    Impulse.received_at <= end_date,
                    Impulse.type == "growth",
                )
            )
            growth_count = await session.scalar(growth_query) or 0

            fall_count = total - growth_count

            # Get unique coins count
            unique_query = select(func.count(func.distinct(Impulse.symbol))).where(
                and_(
                    Impulse.received_at >= start_date,
                    Impulse.received_at <= end_date,
                )
            )
            unique_coins = await session.scalar(unique_query) or 0

            # Get top growth
            top_growth = await self._get_top_impulses(
                session, start_date, end_date, "growth", 5
            )

            # Get top fall
            top_fall = await self._get_top_impulses(
                session, start_date, end_date, "fall", 5
            )

            # Get comparison data
            comparison = await self._get_comparison(session, period, total)

        return AnalyticsResponse(
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_impulses=total,
            growth_count=growth_count,
            fall_count=fall_count,
            unique_coins=unique_coins,
            top_growth=top_growth,
            top_fall=top_fall,
            comparison=comparison,
        )

    def _get_period_dates(self, period: str) -> tuple[datetime, datetime]:
        """Get start and end dates for period.

        Args:
            period: Period identifier

        Returns:
            Tuple of (start_date, end_date)
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if period == AnalyticsPeriod.TODAY.value:
            start_date = today_start
            end_date = now
        elif period == AnalyticsPeriod.YESTERDAY.value:
            start_date = today_start - timedelta(days=1)
            end_date = today_start - timedelta(seconds=1)
        elif period == AnalyticsPeriod.WEEK.value:
            start_date = today_start - timedelta(days=7)
            end_date = now
        elif period == AnalyticsPeriod.MONTH.value:
            start_date = today_start - timedelta(days=30)
            end_date = now
        else:
            start_date = today_start
            end_date = now

        return start_date, end_date

    async def _get_top_impulses(
        self,
        session,
        start_date: datetime,
        end_date: datetime,
        impulse_type: str,
        limit: int,
    ) -> list[TopImpulse]:
        """Get top impulses by type.

        Args:
            session: Database session
            start_date: Period start
            end_date: Period end
            impulse_type: Type of impulse (growth/fall)
            limit: Maximum number of results

        Returns:
            List of top impulses
        """
        # Get symbols with max percent and count
        query = (
            select(
                Impulse.symbol,
                func.max(func.abs(Impulse.percent)).label("max_percent"),
                func.count().label("count"),
            )
            .where(
                and_(
                    Impulse.received_at >= start_date,
                    Impulse.received_at <= end_date,
                    Impulse.type == impulse_type,
                )
            )
            .group_by(Impulse.symbol)
            .order_by(func.max(func.abs(Impulse.percent)).desc())
            .limit(limit)
        )

        result = await session.execute(query)
        rows = result.all()

        return [
            TopImpulse(
                symbol=row.symbol,
                percent=Decimal(str(row.max_percent)) * (-1 if impulse_type == "fall" else 1),
                count=row.count,
            )
            for row in rows
        ]

    async def _get_daily_counts(
        self, session, start_date: datetime, end_date: datetime
    ) -> list[int]:
        """Get impulse counts per day for a date range."""
        query = (
            select(
                cast(Impulse.received_at, Date).label("day"),
                func.count().label("cnt"),
            )
            .where(
                and_(
                    Impulse.received_at >= start_date,
                    Impulse.received_at <= end_date,
                )
            )
            .group_by(cast(Impulse.received_at, Date))
        )
        result = await session.execute(query)
        return [row.cnt for row in result.all()]

    async def _get_comparison(
        self,
        session,
        period: str,
        current_total: int,
    ) -> Optional[ComparisonData]:
        """Get comparison data for any period."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        yesterday_total = None
        vs_yesterday = None
        week_median = None
        vs_week_median = None
        month_median = None
        vs_month_median = None

        if period == AnalyticsPeriod.TODAY.value:
            # Compare today with yesterday
            yesterday_start = today_start - timedelta(days=1)
            yesterday_end = today_start - timedelta(seconds=1)
            yq = select(func.count()).where(
                and_(
                    Impulse.received_at >= yesterday_start,
                    Impulse.received_at <= yesterday_end,
                )
            )
            yesterday_total = await session.scalar(yq) or 0

            if yesterday_total > 0:
                change = ((current_total - yesterday_total) / yesterday_total) * 100
                vs_yesterday = f"{change:+.1f}%"
            else:
                vs_yesterday = "нет данных"

        elif period == AnalyticsPeriod.YESTERDAY.value:
            # Compare yesterday with the day before yesterday
            day_before_start = today_start - timedelta(days=2)
            day_before_end = today_start - timedelta(days=1, seconds=1)
            dbq = select(func.count()).where(
                and_(
                    Impulse.received_at >= day_before_start,
                    Impulse.received_at <= day_before_end,
                )
            )
            yesterday_total = await session.scalar(dbq) or 0

            if yesterday_total > 0:
                change = ((current_total - yesterday_total) / yesterday_total) * 100
                vs_yesterday = f"{change:+.1f}%"
            else:
                vs_yesterday = "нет данных"

        # Week median (daily counts for last 14 days)
        week_start = today_start - timedelta(days=14)
        week_counts = await self._get_daily_counts(session, week_start, today_start - timedelta(seconds=1))
        if week_counts:
            week_median = int(statistics.median(week_counts))
            if week_median > 0:
                if current_total > week_median * 1.5:
                    vs_week_median = "высокая активность"
                elif current_total < week_median * 0.5:
                    vs_week_median = "низкая активность"
                else:
                    vs_week_median = "в норме"
            else:
                vs_week_median = "нет данных"
        else:
            week_median = 0
            vs_week_median = "нет данных"

        # Month median (daily counts for last 30 days)
        month_start = today_start - timedelta(days=30)
        month_counts = await self._get_daily_counts(session, month_start, today_start - timedelta(seconds=1))
        if month_counts:
            month_median = int(statistics.median(month_counts))
            if month_median > 0:
                if current_total > month_median * 1.5:
                    vs_month_median = "высокая активность"
                elif current_total < month_median * 0.5:
                    vs_month_median = "низкая активность"
                else:
                    vs_month_median = "в норме"
            else:
                vs_month_median = "нет данных"
        else:
            month_median = 0
            vs_month_median = "нет данных"

        return ComparisonData(
            vs_yesterday=vs_yesterday,
            yesterday_total=yesterday_total,
            vs_week_median=vs_week_median,
            week_median=week_median,
            vs_month_median=vs_month_median,
            month_median=month_median,
        )


    async def get_time_series(self, period: str) -> dict:
        """Get signal counts as time series.

        Args:
            period: Period identifier (today, week, month)

        Returns:
            Time series data with labels and counts
        """
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Convert timestamp to local timezone for correct hour/day extraction
        local_time = func.timezone(settings.TIMEZONE, Impulse.received_at)

        async with async_session_maker() as session:
            if period == "today":
                # Hourly counts for today (using local timezone)
                query = (
                    select(
                        extract("hour", local_time).label("hour"),
                        func.count().label("count"),
                    )
                    .where(Impulse.received_at >= today_start)
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
                    .where(Impulse.received_at >= week_start)
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
                    .where(Impulse.received_at >= month_start)
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

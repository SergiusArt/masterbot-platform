"""Analytics service for impulse data analysis."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, and_

from models.impulse import Impulse
from shared.database.connection import async_session_maker
from shared.schemas.impulse import AnalyticsResponse, TopImpulse, ComparisonData
from shared.constants import AnalyticsPeriod


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

    async def _get_comparison(
        self,
        session,
        period: str,
        current_total: int,
    ) -> Optional[ComparisonData]:
        """Get comparison data.

        Args:
            session: Database session
            period: Current period
            current_total: Current period total

        Returns:
            Comparison data or None
        """
        if period != AnalyticsPeriod.TODAY.value:
            return None

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Yesterday's total
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start - timedelta(seconds=1)

        yesterday_query = select(func.count()).where(
            and_(
                Impulse.received_at >= yesterday_start,
                Impulse.received_at <= yesterday_end,
            )
        )
        yesterday_total = await session.scalar(yesterday_query) or 0

        # Calculate comparison
        if yesterday_total > 0:
            change = ((current_total - yesterday_total) / yesterday_total) * 100
            vs_yesterday = f"{change:+.0f}%"
        else:
            vs_yesterday = "N/A"

        return ComparisonData(
            vs_yesterday=vs_yesterday,
            vs_week_median="N/A",
            vs_month_median="N/A",
        )


# Global service instance
analytics_service = AnalyticsService()

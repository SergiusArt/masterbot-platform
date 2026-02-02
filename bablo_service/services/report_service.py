"""Report service for Bablo signals."""

from datetime import datetime, timedelta
from typing import Optional
import pytz

from sqlalchemy.ext.asyncio import AsyncSession

from services.signal_service import signal_service
from services.analytics_service import analytics_service
from config import settings
from shared.utils.logger import get_logger

logger = get_logger("bablo_report_service")


class ReportService:
    """Service for generating Bablo reports."""

    def __init__(self):
        self.tz = pytz.timezone(settings.TIMEZONE)

    async def generate_report(
        self,
        session: AsyncSession,
        report_type: str,
    ) -> dict:
        """Generate report of specified type.

        Args:
            session: Database session
            report_type: Report type ('morning', 'evening', 'weekly', 'monthly')

        Returns:
            Report dictionary with title and text
        """
        if report_type == "morning":
            return await self._generate_morning_report(session)
        elif report_type == "evening":
            return await self._generate_evening_report(session)
        elif report_type == "weekly":
            return await self._generate_weekly_report(session)
        elif report_type == "monthly":
            return await self._generate_monthly_report(session)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    async def _generate_morning_report(self, session: AsyncSession) -> dict:
        """Generate morning report (yesterday's summary)."""
        analytics = await analytics_service.get_analytics(session, "yesterday")

        title = "🌅 Утренний отчёт Bablo"
        text = self._format_report(analytics, "за вчера")

        return {
            "title": title,
            "text": text,
            "type": "morning",
            "generated_at": datetime.now(self.tz).isoformat(),
        }

    async def _generate_evening_report(self, session: AsyncSession) -> dict:
        """Generate evening report (today's summary)."""
        analytics = await analytics_service.get_analytics(session, "today")
        comparison = await analytics_service.get_comparison(session)

        title = "🌆 Вечерний отчёт Bablo"
        text = self._format_report(analytics, "за сегодня", comparison)

        return {
            "title": title,
            "text": text,
            "type": "evening",
            "generated_at": datetime.now(self.tz).isoformat(),
        }

    async def _generate_weekly_report(self, session: AsyncSession) -> dict:
        """Generate weekly report (last 7 days)."""
        analytics = await analytics_service.get_analytics(session, "week")

        title = "📊 Недельный отчёт Bablo"
        text = self._format_report(analytics, "за неделю")

        return {
            "title": title,
            "text": text,
            "type": "weekly",
            "generated_at": datetime.now(self.tz).isoformat(),
        }

    async def _generate_monthly_report(self, session: AsyncSession) -> dict:
        """Generate monthly report (last 30 days)."""
        analytics = await analytics_service.get_analytics(session, "month")

        title = "📊 Месячный отчёт Bablo"
        text = self._format_report(analytics, "за месяц")

        return {
            "title": title,
            "text": text,
            "type": "monthly",
            "generated_at": datetime.now(self.tz).isoformat(),
        }

    def _format_report(
        self,
        analytics: dict,
        period_label: str,
        comparison: Optional[dict] = None,
    ) -> str:
        """Format analytics data into report text."""
        total = analytics["total_signals"]
        long_count = analytics["long_count"]
        short_count = analytics["short_count"]
        avg_quality = analytics.get("average_quality")

        lines = [
            f"📊 Сигналов {period_label}: <b>{total}</b>",
            f"🟢 Long: {long_count} | 🔴 Short: {short_count}",
        ]

        # Timeframe breakdown
        by_tf = analytics.get("by_timeframe", {})
        if by_tf:
            lines.append("")
            lines.append("📈 <b>По таймфреймам:</b>")
            for tf, count in sorted(by_tf.items()):
                lines.append(f"  • {tf}: {count}")

        # Average quality
        if avg_quality:
            lines.append("")
            lines.append(f"⭐ Средний показатель качества: <b>{avg_quality}</b>")

        # Top symbols
        top_symbols = analytics.get("top_symbols", [])
        if top_symbols:
            lines.append("")
            lines.append("🏆 <b>Топ символы:</b>")
            for item in top_symbols[:5]:
                lines.append(f"  • {item['symbol']}: {item['count']}")

        # Comparison (for evening report)
        if comparison:
            lines.append("")
            vs_yesterday = comparison.get("vs_yesterday", "—")
            vs_week = comparison.get("vs_week_avg", "—")
            lines.append(f"📊 vs вчера: {vs_yesterday} | vs неделя: {vs_week}")

        return "\n".join(lines)

    async def get_report_data(
        self,
        session: AsyncSession,
        report_type: str,
    ) -> dict:
        """Get raw report data for aggregation with other services.

        Args:
            session: Database session
            report_type: Report type

        Returns:
            Raw report data dictionary
        """
        period_map = {
            "morning": "yesterday",
            "evening": "today",
            "weekly": "week",
            "monthly": "month",
        }

        period = period_map.get(report_type, "today")
        analytics = await analytics_service.get_analytics(session, period)

        return {
            "service": "bablo",
            "report_type": report_type,
            "analytics": analytics,
            "formatted_text": self._format_report(
                analytics,
                self._get_period_label(report_type),
            ),
            "generated_at": datetime.now(self.tz).isoformat(),
        }

    def _get_period_label(self, report_type: str) -> str:
        """Get period label for report type."""
        labels = {
            "morning": "за вчера",
            "evening": "за сегодня",
            "weekly": "за неделю",
            "monthly": "за месяц",
        }
        return labels.get(report_type, "")


# Global service instance
report_service = ReportService()

"""Report generation service."""

from datetime import datetime, timezone

from services.analytics_service import analytics_service
from shared.schemas.impulse import ReportData
from shared.constants import ReportType


class ReportService:
    """Service for generating reports."""

    async def generate_report(self, report_type: str, user_id: int) -> ReportData:
        """Generate report for user."""
        if report_type == ReportType.MORNING.value:
            return await self._generate_morning_report()
        elif report_type == ReportType.EVENING.value:
            return await self._generate_evening_report()
        elif report_type == ReportType.WEEKLY.value:
            return await self._generate_weekly_report()
        elif report_type == ReportType.MONTHLY.value:
            return await self._generate_monthly_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _format_header(self, analytics, period_label: str) -> list[str]:
        """Format common header lines."""
        lines = [
            f"Импульсов {period_label}: <b>{analytics.total_impulses}</b>",
            f"🟢 Роста: <b>{analytics.growth_count}</b>",
            f"🔴 Падения: <b>{analytics.fall_count}</b>",
            f"📈 Уникальных монет: <b>{analytics.unique_coins}</b>",
        ]
        return lines

    def _format_comparison(self, analytics, prev_day_label: str = "Вчера") -> list[str]:
        """Format comparison section.

        Args:
            analytics: Analytics data with comparison
            prev_day_label: Label for the previous period comparison (e.g., "Вчера", "Позавчера")
        """
        lines = []
        comp = analytics.comparison
        if not comp:
            return lines

        lines.append("")
        lines.append("<b>📊 Сравнения:</b>")

        if comp.yesterday_total is not None and comp.vs_yesterday:
            lines.append(f"  • {prev_day_label}: {comp.yesterday_total} ({comp.vs_yesterday})")

        if comp.week_median is not None:
            label = self._activity_emoji(comp.vs_week_median)
            lines.append(f"  • Медиана недели: {comp.week_median} — {label}")

        if comp.month_median is not None:
            label = self._activity_emoji(comp.vs_month_median)
            lines.append(f"  • Медиана месяца: {comp.month_median} — {label}")

        return lines

    def _activity_emoji(self, label: str) -> str:
        """Add emoji to activity label."""
        mapping = {
            "высокая активность": "🟡 высокая активность",
            "низкая активность": "🔵 низкая активность",
            "в норме": "🟢 в норме",
            "нет данных": "📊 нет данных",
        }
        return mapping.get(label, label)

    def _format_top(self, analytics, period_word: str) -> list[str]:
        """Format top leaders."""
        lines = []
        if analytics.top_growth:
            lines.append("")
            lines.append(f"<b>🏆 Лидеры {period_word} (рост):</b>")
            for i, item in enumerate(analytics.top_growth[:3], 1):
                lines.append(f"  {i}. {item.symbol}: <b>+{item.percent:.1f}%</b>")

        if analytics.top_fall:
            lines.append("")
            lines.append(f"<b>📉 Лидеры {period_word} (падение):</b>")
            for i, item in enumerate(analytics.top_fall[:3], 1):
                lines.append(f"  {i}. {item.symbol}: <b>{item.percent:.1f}%</b>")

        return lines

    async def _generate_morning_report(self) -> ReportData:
        """Generate morning report (yesterday's summary)."""
        analytics = await analytics_service.get_analytics("yesterday")

        lines = self._format_header(analytics, "за вчера")
        lines += self._format_comparison(analytics, prev_day_label="Позавчера")
        lines += self._format_top(analytics, "дня")

        return ReportData(
            title="🌅 Утренний отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )

    async def _generate_evening_report(self) -> ReportData:
        """Generate evening report (today's summary)."""
        analytics = await analytics_service.get_analytics("today")

        lines = self._format_header(analytics, "за сегодня")
        lines += self._format_comparison(analytics)
        lines += self._format_top(analytics, "дня")

        return ReportData(
            title="🌆 Вечерний отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )

    async def _generate_weekly_report(self) -> ReportData:
        """Generate weekly report."""
        analytics = await analytics_service.get_analytics("week")

        lines = self._format_header(analytics, "за неделю")
        lines += self._format_comparison(analytics)
        lines += self._format_top(analytics, "недели")

        return ReportData(
            title="📊 Недельный отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )

    async def _generate_monthly_report(self) -> ReportData:
        """Generate monthly report."""
        analytics = await analytics_service.get_analytics("month")

        lines = self._format_header(analytics, "за месяц")
        lines += self._format_comparison(analytics)
        lines += self._format_top(analytics, "месяца")

        return ReportData(
            title="📊 Месячный отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )


# Global service instance
report_service = ReportService()

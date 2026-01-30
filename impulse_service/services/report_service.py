"""Report generation service."""

from datetime import datetime, timezone

from services.analytics_service import analytics_service
from shared.schemas.impulse import ReportData
from shared.constants import ReportType


class ReportService:
    """Service for generating reports."""

    async def generate_report(self, report_type: str, user_id: int) -> ReportData:
        """Generate report for user.

        Args:
            report_type: Type of report
            user_id: User ID

        Returns:
            Generated report data
        """
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

    async def _generate_morning_report(self) -> ReportData:
        """Generate morning report."""
        # Get yesterday's analytics
        analytics = await analytics_service.get_analytics("yesterday")

        lines = [
            f"📊 Импульсов за вчера: <b>{analytics.total_impulses}</b>",
            f"🟢 Рост: <b>{analytics.growth_count}</b>",
            f"🔴 Падение: <b>{analytics.fall_count}</b>",
        ]

        if analytics.top_growth:
            lines.append("\n<b>🏆 Топ рост:</b>")
            for item in analytics.top_growth[:3]:
                lines.append(f"  • {item.symbol}: <b>+{item.percent:.1f}%</b>")

        if analytics.top_fall:
            lines.append("\n<b>📉 Топ падение:</b>")
            for item in analytics.top_fall[:3]:
                lines.append(f"  • {item.symbol}: <b>{item.percent:.1f}%</b>")

        lines.append("\n💡 Хорошего дня!")

        return ReportData(
            title="🌅 Утренний отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )

    async def _generate_evening_report(self) -> ReportData:
        """Generate evening report."""
        # Get today's analytics
        analytics = await analytics_service.get_analytics("today")

        lines = [
            f"📊 Импульсов за сегодня: <b>{analytics.total_impulses}</b>",
            f"🟢 Рост: <b>{analytics.growth_count}</b>",
            f"🔴 Падение: <b>{analytics.fall_count}</b>",
        ]

        if analytics.top_growth:
            lines.append("\n<b>🏆 Лидеры роста:</b>")
            for item in analytics.top_growth[:3]:
                lines.append(f"  • {item.symbol}: <b>+{item.percent:.1f}%</b>")

        if analytics.top_fall:
            lines.append("\n<b>📉 Лидеры падения:</b>")
            for item in analytics.top_fall[:3]:
                lines.append(f"  • {item.symbol}: <b>{item.percent:.1f}%</b>")

        if analytics.comparison:
            lines.append(f"\n📈 По сравнению с вчера: {analytics.comparison.vs_yesterday}")

        lines.append("\n💤 Хорошего вечера!")

        return ReportData(
            title="🌆 Вечерний отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )

    async def _generate_weekly_report(self) -> ReportData:
        """Generate weekly report."""
        analytics = await analytics_service.get_analytics("week")

        lines = [
            f"📈 Всего импульсов: <b>{analytics.total_impulses}</b>",
            f"🟢 Рост: <b>{analytics.growth_count}</b>",
            f"🔴 Падение: <b>{analytics.fall_count}</b>",
        ]

        if analytics.top_growth:
            lines.append("\n<b>🏆 Топ-5 рост за неделю:</b>")
            for item in analytics.top_growth:
                lines.append(f"  • {item.symbol}: <b>+{item.percent:.1f}%</b> ({item.count}x)")

        if analytics.top_fall:
            lines.append("\n<b>📉 Топ-5 падение за неделю:</b>")
            for item in analytics.top_fall:
                lines.append(f"  • {item.symbol}: <b>{item.percent:.1f}%</b> ({item.count}x)")

        return ReportData(
            title="📊 Недельный отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )

    async def _generate_monthly_report(self) -> ReportData:
        """Generate monthly report."""
        analytics = await analytics_service.get_analytics("month")

        lines = [
            f"📈 Всего импульсов: <b>{analytics.total_impulses}</b>",
            f"🟢 Рост: <b>{analytics.growth_count}</b>",
            f"🔴 Падение: <b>{analytics.fall_count}</b>",
        ]

        if analytics.top_growth:
            lines.append("\n<b>🏆 Топ-5 рост за месяц:</b>")
            for item in analytics.top_growth:
                lines.append(f"  • {item.symbol}: <b>+{item.percent:.1f}%</b> ({item.count}x)")

        if analytics.top_fall:
            lines.append("\n<b>📉 Топ-5 падение за месяц:</b>")
            for item in analytics.top_fall:
                lines.append(f"  • {item.symbol}: <b>{item.percent:.1f}%</b> ({item.count}x)")

        return ReportData(
            title="📊 Месячный отчёт",
            text="\n".join(lines),
            generated_at=datetime.now(timezone.utc),
        )


# Global service instance
report_service = ReportService()

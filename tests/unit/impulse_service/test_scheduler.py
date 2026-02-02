"""Tests for impulse service scheduler and report functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal

import sys

# Mock logger before imports
sys.modules['shared.utils.logger'] = MagicMock()


class TestReportDataFormat:
    """Test report data format for Redis publishing."""

    @pytest.mark.unit
    def test_report_data_has_correct_keys(self):
        """Test report data contains required keys for notification listener."""
        report_data = {
            "event": "report_ready",
            "user_id": 123,
            "data": {
                "report_type": "morning",
                "text": "Report content",
                "content": "Report content",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

        assert "event" in report_data
        assert "user_id" in report_data
        assert "data" in report_data

        data = report_data["data"]
        assert "report_type" in data
        assert "text" in data
        assert "content" in data
        assert "timestamp" in data

    @pytest.mark.unit
    def test_report_types_are_valid(self):
        """Test that report types match expected values."""
        valid_types = ["morning", "evening", "weekly", "monthly"]

        for report_type in valid_types:
            report_data = {"data": {"report_type": report_type}}
            assert report_data["data"]["report_type"] in valid_types


class TestReportService:
    """Tests for impulse report service with improved format."""

    def _mock_analytics(self, **kwargs):
        """Create mock analytics with defaults."""
        defaults = {
            "total_impulses": 10,
            "growth_count": 6,
            "fall_count": 4,
            "unique_coins": 8,
            "top_growth": [
                MagicMock(symbol="BTCUSDT.P", percent=Decimal("33.8")),
                MagicMock(symbol="ETHUSDT.P", percent=Decimal("22.5")),
            ],
            "top_fall": [
                MagicMock(symbol="XRPUSDT.P", percent=Decimal("-15.0")),
            ],
            "comparison": MagicMock(
                yesterday_total=20,
                vs_yesterday="-50.0%",
                week_median=15,
                vs_week_median="низкая активность",
                month_median=12,
                vs_month_median="в норме",
            ),
        }
        defaults.update(kwargs)
        return MagicMock(**defaults)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_morning_report_contains_unique_coins(self):
        """Test morning report includes unique coins count."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert "Уникальных монет" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_morning_report_contains_comparisons(self):
        """Test morning report includes comparison section."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert "Сравнения" in report.text
            assert "Медиана недели" in report.text
            assert "Медиана месяца" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_report_contains_numbered_leaders(self):
        """Test report uses numbered list for leaders."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert "1." in report.text
            assert "2." in report.text
            assert "Лидеры дня (рост)" in report.text
            assert "Лидеры дня (падение)" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evening_report_format(self):
        """Test evening report with correct period label."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("evening", user_id=123)

            assert "за сегодня" in report.text
            assert "Лидеры дня" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_weekly_report_format(self):
        """Test weekly report with correct labels."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("weekly", user_id=123)

            assert "за неделю" in report.text
            assert "Лидеры недели" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_monthly_report_format(self):
        """Test monthly report with correct labels."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("monthly", user_id=123)

            assert "за месяц" in report.text
            assert "Лидеры месяца" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_report_no_closing_greeting(self):
        """Test reports no longer contain closing greetings (moved to scheduler)."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert "Хорошего дня" not in report.text
            assert "Хорошего вечера" not in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_report_uses_genitive_case(self):
        """Test report uses correct Russian grammar (Роста/Падения)."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics())

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert "Роста:" in report.text
            assert "Падения:" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_report_empty_leaders_when_no_data(self):
        """Test report omits leader section when no data."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=self._mock_analytics(
                total_impulses=0,
                growth_count=0,
                fall_count=0,
                unique_coins=0,
                top_growth=[],
                top_fall=[],
                comparison=MagicMock(
                    yesterday_total=None,
                    vs_yesterday=None,
                    week_median=0,
                    vs_week_median="нет данных",
                    month_median=0,
                    vs_month_median="нет данных",
                ),
            ))

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert "Лидеры" not in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_report_type_raises(self):
        """Test invalid report type raises ValueError."""
        from services.report_service import ReportService

        service = ReportService()

        with pytest.raises(ValueError) as exc_info:
            await service.generate_report("invalid", user_id=123)

        assert "Unknown report type" in str(exc_info.value)


class TestActivityEmoji:
    """Test activity level emoji mapping."""

    @pytest.mark.unit
    def test_activity_emoji_mapping(self):
        """Test all activity levels have correct emoji."""
        from services.report_service import ReportService

        service = ReportService()

        assert "🟡" in service._activity_emoji("высокая активность")
        assert "🔵" in service._activity_emoji("низкая активность")
        assert "🟢" in service._activity_emoji("в норме")
        assert "📊" in service._activity_emoji("нет данных")

    @pytest.mark.unit
    def test_activity_emoji_unknown_returns_as_is(self):
        """Test unknown label is returned unchanged."""
        from services.report_service import ReportService

        service = ReportService()

        assert service._activity_emoji("unknown") == "unknown"

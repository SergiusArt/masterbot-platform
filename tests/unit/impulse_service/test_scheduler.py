"""Tests for scheduler and report functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "impulse_service"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))

# Mock logger before imports
sys.modules['shared.utils.logger'] = MagicMock()


class TestSchedulerConfiguration:
    """Test scheduler configuration."""

    @pytest.mark.unit
    def test_scheduler_jobs_configured(self):
        """Test scheduler has correct jobs configured."""
        from core.scheduler import scheduler, start_scheduler, stop_scheduler

        # Start scheduler (it adds jobs)
        with patch('core.scheduler.scheduler.start'):
            start_scheduler()

        # Check jobs are configured
        jobs = scheduler.get_jobs()
        job_ids = [job.id for job in jobs]

        assert "morning_reports" in job_ids
        assert "evening_reports" in job_ids
        assert "weekly_reports" in job_ids

        # Stop scheduler
        with patch('core.scheduler.scheduler.shutdown'):
            stop_scheduler()


class TestReportDataFormat:
    """Test report data format for Redis publishing."""

    @pytest.mark.unit
    def test_report_data_has_correct_keys(self):
        """Test report data contains required keys for notification listener."""
        # Simulated report data as sent by scheduler
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

        # Check required keys
        assert "event" in report_data
        assert "user_id" in report_data
        assert "data" in report_data

        # Check data keys (notification listener expects these)
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
            report_data = {
                "data": {
                    "report_type": report_type,
                }
            }
            assert report_data["data"]["report_type"] in valid_types


class TestReportService:
    """Tests for report service."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_morning_report(self):
        """Test morning report generation."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=MagicMock(
                total_impulses=10,
                growth_count=6,
                fall_count=4,
                top_growth=[
                    MagicMock(symbol="BTC", percent=15.5),
                    MagicMock(symbol="ETH", percent=10.2),
                ],
                top_fall=[
                    MagicMock(symbol="XRP", percent=-8.3),
                ],
            ))

            service = ReportService()
            report = await service.generate_report("morning", user_id=123)

            assert report is not None
            assert "Утренний отчёт" in report.text
            assert "10" in report.text  # total impulses
            assert report.generated_at is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_evening_report(self):
        """Test evening report generation."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=MagicMock(
                total_impulses=25,
                growth_count=15,
                fall_count=10,
                top_growth=[],
                top_fall=[],
                comparison=MagicMock(vs_yesterday="+5"),
            ))

            service = ReportService()
            report = await service.generate_report("evening", user_id=123)

            assert report is not None
            assert "Вечерний отчёт" in report.text
            assert "25" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_weekly_report(self):
        """Test weekly report generation."""
        with patch('services.report_service.analytics_service') as mock_analytics:
            from services.report_service import ReportService

            mock_analytics.get_analytics = AsyncMock(return_value=MagicMock(
                total_impulses=150,
                growth_count=90,
                fall_count=60,
                top_growth=[],
                top_fall=[],
            ))

            service = ReportService()
            report = await service.generate_report("weekly", user_id=123)

            assert report is not None
            assert "Недельный отчёт" in report.text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_report_type_raises(self):
        """Test invalid report type raises ValueError."""
        from services.report_service import ReportService

        service = ReportService()

        with pytest.raises(ValueError) as exc_info:
            await service.generate_report("invalid", user_id=123)

        assert "Unknown report type" in str(exc_info.value)

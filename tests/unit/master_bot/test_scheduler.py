"""Tests for unified report scheduler in master_bot."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "master_bot"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))

# Mock modules that load config on import
_mock_settings = MagicMock()
_mock_settings.TIMEZONE = "Europe/Moscow"
_mock_settings.IMPULSE_SERVICE_URL = "http://localhost:8001"
_mock_settings.BABLO_SERVICE_URL = "http://localhost:8002"
sys.modules['config'] = MagicMock(settings=_mock_settings)
sys.modules['shared.utils.logger'] = MagicMock()
sys.modules['services.impulse_client'] = MagicMock()
sys.modules['services.bablo_client'] = MagicMock()


class TestReportSchedulerInit:
    """Test scheduler initialization and job registration."""

    @pytest.mark.unit
    def test_scheduler_creates_four_jobs(self):
        """Test scheduler registers morning, evening, weekly, monthly jobs."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler

        scheduler = ReportScheduler(mock_bot)

        with patch.object(scheduler.scheduler, 'start'):
            scheduler.start()

        jobs = scheduler.scheduler.get_jobs()
        job_ids = [job.id for job in jobs]

        assert "morning_reports" in job_ids
        assert "evening_reports" in job_ids
        assert "weekly_reports" in job_ids
        assert "monthly_reports" in job_ids
        assert len(job_ids) == 4

    @pytest.mark.unit
    def test_init_scheduler_creates_global_instance(self):
        """Test init_scheduler sets global report_scheduler."""
        mock_bot = MagicMock()

        from services.scheduler import init_scheduler

        scheduler = init_scheduler(mock_bot)
        assert scheduler is not None
        assert scheduler.bot is mock_bot


class TestGetUsersForReport:
    """Test fetching users from both services."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_combines_users_from_both_services(self):
        """Test users are merged from impulse and bablo services."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.get_users_for_report = AsyncMock(return_value=[100, 200])
        mock_bablo = MagicMock()
        mock_bablo.get_users_for_report = AsyncMock(return_value=[200, 300])

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        users = await scheduler._get_users_for_report("morning")

        assert 100 in users
        assert 200 in users
        assert 300 in users
        assert users[100] == {"impulse": True, "bablo": False}
        assert users[200] == {"impulse": True, "bablo": True}
        assert users[300] == {"impulse": False, "bablo": True}

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handles_impulse_service_error(self):
        """Test graceful handling when impulse service is unavailable."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.get_users_for_report = AsyncMock(side_effect=Exception("Connection refused"))
        mock_bablo = MagicMock()
        mock_bablo.get_users_for_report = AsyncMock(return_value=[100])

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        users = await scheduler._get_users_for_report("morning")

        assert 100 in users
        assert users[100]["bablo"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handles_bablo_service_error(self):
        """Test graceful handling when bablo service is unavailable."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.get_users_for_report = AsyncMock(return_value=[100])
        mock_bablo = MagicMock()
        mock_bablo.get_users_for_report = AsyncMock(side_effect=Exception("Connection refused"))

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        users = await scheduler._get_users_for_report("morning")

        assert 100 in users
        assert users[100]["impulse"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_returns_empty_when_both_services_fail(self):
        """Test returns empty dict when both services are down."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.get_users_for_report = AsyncMock(side_effect=Exception("err"))
        mock_bablo = MagicMock()
        mock_bablo.get_users_for_report = AsyncMock(side_effect=Exception("err"))

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        users = await scheduler._get_users_for_report("morning")

        assert users == {}


class TestGenerateCombinedReport:
    """Test combined report generation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_combined_report_both_services(self):
        """Test report includes both impulse and bablo sections."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.generate_report = AsyncMock(return_value={
            "report": {"text": "Импульсов за вчера: 10", "title": "test"}
        })
        mock_bablo = MagicMock()
        mock_bablo.generate_report = AsyncMock(return_value={
            "report": {"text": "Сигналов за вчера: 50", "title": "test"}
        })

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        services = {"impulse": True, "bablo": True}
        report = await scheduler._generate_combined_report(123, "morning", "Утренний отчёт", services)

        assert report is not None
        assert "Импульсы" in report
        assert "Bablo" in report
        assert "Импульсов за вчера: 10" in report
        assert "Сигналов за вчера: 50" in report

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_combined_report_impulse_only(self):
        """Test report with only impulse service (no section headers)."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.generate_report = AsyncMock(return_value={
            "report": {"text": "Импульсов за вчера: 10", "title": "test"}
        })
        sched_module.impulse_client = mock_impulse

        scheduler = ReportScheduler(mock_bot)
        services = {"impulse": True, "bablo": False}
        report = await scheduler._generate_combined_report(123, "morning", "Утренний отчёт", services)

        assert report is not None
        assert "Импульсов за вчера: 10" in report

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_combined_report_returns_none_on_empty(self):
        """Test returns None when no content from services."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.generate_report = AsyncMock(return_value={"report": {"text": ""}})
        mock_bablo = MagicMock()
        mock_bablo.generate_report = AsyncMock(return_value={"report": {"text": ""}})

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        services = {"impulse": True, "bablo": True}
        report = await scheduler._generate_combined_report(123, "morning", "test", services)

        assert report is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_morning_report_has_closing_greeting(self):
        """Test morning report includes closing greeting."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.generate_report = AsyncMock(return_value={
            "report": {"text": "Импульсов: 10", "title": "test"}
        })
        sched_module.impulse_client = mock_impulse

        scheduler = ReportScheduler(mock_bot)
        services = {"impulse": True, "bablo": False}
        report = await scheduler._generate_combined_report(123, "morning", "Утренний отчёт", services)

        assert "Хорошего дня!" in report

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evening_report_has_closing_greeting(self):
        """Test evening report includes closing greeting."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.generate_report = AsyncMock(return_value={
            "report": {"text": "Импульсов: 10", "title": "test"}
        })
        sched_module.impulse_client = mock_impulse

        scheduler = ReportScheduler(mock_bot)
        services = {"impulse": True, "bablo": False}
        report = await scheduler._generate_combined_report(123, "evening", "Вечерний отчёт", services)

        assert "Хорошего вечера!" in report

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_weekly_report_no_closing_greeting(self):
        """Test weekly report has no closing greeting."""
        mock_bot = MagicMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.generate_report = AsyncMock(return_value={
            "report": {"text": "Импульсов: 100", "title": "test"}
        })
        sched_module.impulse_client = mock_impulse

        scheduler = ReportScheduler(mock_bot)
        services = {"impulse": True, "bablo": False}
        report = await scheduler._generate_combined_report(123, "weekly", "Недельный отчёт", services)

        assert "Хорошего" not in report


class TestTriggerReportManually:
    """Test manual report triggering."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_trigger_unknown_type_returns_error(self):
        """Test triggering unknown report type."""
        from services.scheduler import trigger_report_manually, init_scheduler

        mock_bot = MagicMock()
        init_scheduler(mock_bot)

        result = await trigger_report_manually("invalid_type")
        assert "Unknown report type" in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_trigger_without_scheduler_returns_error(self):
        """Test triggering when scheduler is not initialized."""
        import services.scheduler as scheduler_module
        scheduler_module.report_scheduler = None

        result = await scheduler_module.trigger_report_manually("morning")
        assert "not initialized" in result


class TestSendReports:
    """Test the full report sending flow."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_reports_skips_when_no_users(self):
        """Test no messages sent when no users are subscribed."""
        mock_bot = MagicMock()
        mock_bot.send_message = AsyncMock()

        from services.scheduler import ReportScheduler
        import services.scheduler as sched_module

        mock_impulse = MagicMock()
        mock_impulse.get_users_for_report = AsyncMock(return_value=[])
        mock_bablo = MagicMock()
        mock_bablo.get_users_for_report = AsyncMock(return_value=[])

        sched_module.impulse_client = mock_impulse
        sched_module.bablo_client = mock_bablo

        scheduler = ReportScheduler(mock_bot)
        await scheduler._send_reports("morning", "Утренний отчёт")

        mock_bot.send_message.assert_not_called()

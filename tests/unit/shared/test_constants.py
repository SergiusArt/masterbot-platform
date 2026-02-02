"""Unit tests for shared constants."""

import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))


class TestAnalyticsPeriod:
    """Tests for AnalyticsPeriod enum."""

    @pytest.mark.unit
    def test_analytics_period_values(self):
        """Test AnalyticsPeriod enum values."""
        from shared.constants import AnalyticsPeriod

        assert AnalyticsPeriod.TODAY.value == "today"
        assert AnalyticsPeriod.YESTERDAY.value == "yesterday"
        assert AnalyticsPeriod.WEEK.value == "week"
        assert AnalyticsPeriod.MONTH.value == "month"

    @pytest.mark.unit
    def test_analytics_period_members(self):
        """Test all AnalyticsPeriod members exist."""
        from shared.constants import AnalyticsPeriod

        expected_members = ["TODAY", "YESTERDAY", "WEEK", "MONTH"]
        actual_members = [m.name for m in AnalyticsPeriod]

        for member in expected_members:
            assert member in actual_members


class TestImpulseType:
    """Tests for ImpulseType enum."""

    @pytest.mark.unit
    def test_impulse_type_values(self):
        """Test ImpulseType enum values."""
        from shared.constants import ImpulseType

        assert ImpulseType.GROWTH.value == "growth"
        assert ImpulseType.FALL.value == "fall"

    @pytest.mark.unit
    def test_impulse_type_members(self):
        """Test all ImpulseType members."""
        from shared.constants import ImpulseType

        members = [m.value for m in ImpulseType]
        assert "growth" in members
        assert "fall" in members
        assert len(members) == 2


class TestReportType:
    """Tests for ReportType enum."""

    @pytest.mark.unit
    def test_report_type_values(self):
        """Test ReportType enum values."""
        from shared.constants import ReportType

        assert ReportType.MORNING.value == "morning"
        assert ReportType.EVENING.value == "evening"
        assert ReportType.WEEKLY.value == "weekly"
        assert ReportType.MONTHLY.value == "monthly"

    @pytest.mark.unit
    def test_report_type_members(self):
        """Test all ReportType members."""
        from shared.constants import ReportType

        expected = ["MORNING", "EVENING", "WEEKLY", "MONTHLY"]
        actual = [m.name for m in ReportType]

        for member in expected:
            assert member in actual


class TestRedisChannels:
    """Tests for Redis channel constants."""

    @pytest.mark.unit
    def test_redis_channels_defined(self):
        """Test Redis channels are defined."""
        from shared.constants import (
            REDIS_CHANNEL_NOTIFICATIONS,
            REDIS_CHANNEL_ACTIVITY,
            REDIS_CHANNEL_REPORTS,
            REDIS_CHANNEL_BABLO,
        )

        assert isinstance(REDIS_CHANNEL_NOTIFICATIONS, str)
        assert isinstance(REDIS_CHANNEL_ACTIVITY, str)
        assert isinstance(REDIS_CHANNEL_REPORTS, str)
        assert isinstance(REDIS_CHANNEL_BABLO, str)

    @pytest.mark.unit
    def test_redis_channel_values_are_strings(self):
        """Test Redis channel values contain service prefixes."""
        from shared.constants import (
            REDIS_CHANNEL_NOTIFICATIONS,
            REDIS_CHANNEL_REPORTS,
            REDIS_CHANNEL_BABLO,
        )

        assert "impulse" in REDIS_CHANNEL_NOTIFICATIONS
        assert "impulse" in REDIS_CHANNEL_REPORTS
        assert "bablo" in REDIS_CHANNEL_BABLO


class TestDefaultThresholds:
    """Tests for default threshold constants."""

    @pytest.mark.unit
    def test_default_growth_threshold(self):
        """Test default growth threshold is reasonable."""
        from shared.constants import DEFAULT_GROWTH_THRESHOLD

        assert DEFAULT_GROWTH_THRESHOLD > 0
        assert DEFAULT_GROWTH_THRESHOLD <= 100

    @pytest.mark.unit
    def test_default_fall_threshold(self):
        """Test default fall threshold is negative."""
        from shared.constants import DEFAULT_FALL_THRESHOLD

        assert DEFAULT_FALL_THRESHOLD < 0
        assert DEFAULT_FALL_THRESHOLD >= -100


class TestMenuButtons:
    """Tests for menu button text constants."""

    @pytest.mark.unit
    def test_main_menu_buttons_defined(self):
        """Test main menu button texts are defined."""
        from shared.constants import (
            MENU_MAIN,
            MENU_BACK,
            MENU_IMPULSES,
            MENU_BABLO,
            MENU_REPORTS,
            MENU_SETTINGS,
            MENU_ADMIN,
        )

        assert isinstance(MENU_MAIN, str) and len(MENU_MAIN) > 0
        assert isinstance(MENU_BACK, str) and len(MENU_BACK) > 0
        assert isinstance(MENU_IMPULSES, str) and len(MENU_IMPULSES) > 0
        assert isinstance(MENU_BABLO, str) and len(MENU_BABLO) > 0
        assert isinstance(MENU_REPORTS, str) and len(MENU_REPORTS) > 0
        assert isinstance(MENU_SETTINGS, str) and len(MENU_SETTINGS) > 0
        assert isinstance(MENU_ADMIN, str) and len(MENU_ADMIN) > 0

    @pytest.mark.unit
    def test_impulse_menu_buttons_defined(self):
        """Test impulse sub-menu button texts are defined."""
        from shared.constants import (
            MENU_ANALYTICS,
            MENU_NOTIFICATIONS,
            MENU_ACTIVITY,
        )

        assert isinstance(MENU_ANALYTICS, str) and len(MENU_ANALYTICS) > 0
        assert isinstance(MENU_NOTIFICATIONS, str) and len(MENU_NOTIFICATIONS) > 0
        assert isinstance(MENU_ACTIVITY, str) and len(MENU_ACTIVITY) > 0


class TestEventTypes:
    """Tests for event type constants."""

    @pytest.mark.unit
    def test_event_types_defined(self):
        """Test event types are defined."""
        from shared.constants import (
            EVENT_IMPULSE_ALERT,
            EVENT_ACTIVITY_ALERT,
            EVENT_REPORT_READY,
            EVENT_BABLO_SIGNAL,
            EVENT_BABLO_ACTIVITY,
        )

        assert isinstance(EVENT_IMPULSE_ALERT, str)
        assert isinstance(EVENT_ACTIVITY_ALERT, str)
        assert isinstance(EVENT_REPORT_READY, str)
        assert isinstance(EVENT_BABLO_SIGNAL, str)
        assert isinstance(EVENT_BABLO_ACTIVITY, str)

    @pytest.mark.unit
    def test_event_types_are_strings(self):
        """Test event type values follow naming convention."""
        from shared.constants import (
            EVENT_IMPULSE_ALERT,
            EVENT_BABLO_SIGNAL,
        )

        assert "impulse" in EVENT_IMPULSE_ALERT
        assert "bablo" in EVENT_BABLO_SIGNAL

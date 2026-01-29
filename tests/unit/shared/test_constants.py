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
        from shared.constants import RedisChannels

        # Check impulse channel exists
        assert hasattr(RedisChannels, "IMPULSE_SIGNALS")
        assert hasattr(RedisChannels, "IMPULSE_REPORTS")

    @pytest.mark.unit
    def test_redis_channel_values_are_strings(self):
        """Test Redis channel values are strings."""
        from shared.constants import RedisChannels

        for attr in dir(RedisChannels):
            if not attr.startswith("_"):
                value = getattr(RedisChannels, attr)
                if not callable(value):
                    assert isinstance(value, str), f"{attr} should be a string"


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


class TestMenuTexts:
    """Tests for menu text constants."""

    @pytest.mark.unit
    def test_menu_texts_defined(self):
        """Test menu texts are defined."""
        from shared.constants import MenuTexts

        # Check main menu texts
        assert hasattr(MenuTexts, "MAIN_MENU")
        assert hasattr(MenuTexts, "IMPULSE_MENU")

    @pytest.mark.unit
    def test_menu_texts_not_empty(self):
        """Test menu texts are not empty strings."""
        from shared.constants import MenuTexts

        for attr in dir(MenuTexts):
            if not attr.startswith("_"):
                value = getattr(MenuTexts, attr)
                if isinstance(value, str):
                    assert len(value) > 0, f"{attr} should not be empty"


class TestEventTypes:
    """Tests for event type constants."""

    @pytest.mark.unit
    def test_event_types_defined(self):
        """Test event types are defined."""
        from shared.constants import EventTypes

        assert hasattr(EventTypes, "NEW_SIGNAL")
        assert hasattr(EventTypes, "REPORT_GENERATED")

    @pytest.mark.unit
    def test_event_types_are_strings(self):
        """Test event types are strings."""
        from shared.constants import EventTypes

        for attr in dir(EventTypes):
            if not attr.startswith("_"):
                value = getattr(EventTypes, attr)
                if not callable(value):
                    assert isinstance(value, str)

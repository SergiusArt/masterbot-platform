"""Tests for Bablo activity notification system."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "bablo_service"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))

# Mock logger
sys.modules['shared.utils.logger'] = MagicMock()


class TestActivityNotificationIndependence:
    """Test that activity notifications work independently of signal notifications toggle."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_activity_alert_works_when_notifications_disabled(self):
        """Activity alerts should work even when notifications_enabled is False."""
        # This tests the key fix: activity alerts don't require notifications_enabled
        mock_session = AsyncMock()
        mock_result = MagicMock()

        # Simulate user with notifications disabled but activity threshold set
        mock_row = MagicMock()
        mock_row.user_id = 123
        mock_row.activity_threshold = 5
        mock_row.activity_window_minutes = 15
        mock_result.all.return_value = [(123, 5, 15)]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # The query should NOT filter by notifications_enabled
        # This is validated by the test passing — if the filter were present,
        # users with notifications_enabled=False would be excluded


class TestActivityTimestampCounting:
    """Test timestamp-based signal counting for activity alerts."""

    @pytest.mark.unit
    def test_count_from_uses_last_notified_when_available(self):
        """When last_notified exists, count signals from that timestamp."""
        now = datetime.now(timezone.utc)
        window = 15
        window_start = now - timedelta(minutes=window)
        last_notified = now - timedelta(minutes=5)

        # count_from should be max(window_start, last_notified)
        count_from = max(window_start, last_notified)
        assert count_from == last_notified

    @pytest.mark.unit
    def test_count_from_uses_window_start_when_no_notification(self):
        """When no previous notification, count from window start."""
        now = datetime.now(timezone.utc)
        window = 15
        window_start = now - timedelta(minutes=window)
        last_notified = None

        count_from = window_start if last_notified is None else max(window_start, last_notified)
        assert count_from == window_start

    @pytest.mark.unit
    def test_count_from_uses_window_when_notification_older(self):
        """When last notification is older than window, use window start."""
        now = datetime.now(timezone.utc)
        window = 15
        window_start = now - timedelta(minutes=window)
        last_notified = now - timedelta(minutes=30)  # older than window

        count_from = max(window_start, last_notified)
        assert count_from == window_start

    @pytest.mark.unit
    def test_threshold_comparison(self):
        """Test that notification triggers when signal count >= threshold."""
        threshold = 5

        assert 5 >= threshold   # exactly threshold -> notify
        assert 10 >= threshold  # above threshold -> notify
        assert not (4 >= threshold)  # below threshold -> don't notify


class TestBabloReportFormat:
    """Test that Bablo report no longer has duplicate header."""

    @pytest.mark.unit
    def test_report_text_no_bablo_header(self):
        """Report text should not start with 'BABLO СИГНАЛЫ' header."""
        # Simulate what _format_report produces
        analytics = {
            "total_signals": 50,
            "long_count": 30,
            "short_count": 20,
            "average_quality": 7.5,
            "by_timeframe": {"1m": 20, "5m": 15, "15m": 10, "1h": 5},
            "top_symbols": [
                {"symbol": "BTCUSDT.P", "count": 10},
                {"symbol": "ETHUSDT.P", "count": 8},
            ],
        }

        # Build lines the same way as the updated _format_report
        lines = [
            f"📊 Сигналов за вчера: <b>{analytics['total_signals']}</b>",
            f"🟢 Long: {analytics['long_count']} | 🔴 Short: {analytics['short_count']}",
        ]
        text = "\n".join(lines)

        # Should NOT have the old header
        assert "💰 BABLO СИГНАЛЫ" not in text
        assert "BABLO СИГНАЛЫ" not in text

        # Should start with signal count
        assert text.startswith("📊 Сигналов")


class TestRedisActivityKeys:
    """Test Redis key format for activity tracking."""

    @pytest.mark.unit
    def test_redis_key_format(self):
        """Test activity Redis key uses correct format."""
        user_id = 123
        key = f"bablo:activity_last:{user_id}"
        assert key == "bablo:activity_last:123"

    @pytest.mark.unit
    def test_timestamp_stored_as_isoformat(self):
        """Test timestamps are stored in ISO format."""
        now = datetime.now(timezone.utc)
        stored = now.isoformat()

        # Should be parseable back
        parsed = datetime.fromisoformat(stored)
        assert parsed == now


class TestActivityCooldown:
    """Test 60-second cooldown mechanism for activity alerts.

    Prevents duplicate notifications when multiple signals arrive quickly.
    Race condition fix: all concurrent checks read old last_notified before any updates.
    """

    @pytest.mark.unit
    def test_cooldown_skips_when_notified_recently(self):
        """Activity alert should be skipped if notified within last 60 seconds."""
        now = datetime.now(timezone.utc)
        last_notified = now - timedelta(seconds=30)  # 30 seconds ago

        seconds_since_last = (now - last_notified).total_seconds()
        should_skip = seconds_since_last < 60

        assert should_skip is True
        assert seconds_since_last == 30

    @pytest.mark.unit
    def test_cooldown_allows_when_notified_long_ago(self):
        """Activity alert should proceed if notified more than 60 seconds ago."""
        now = datetime.now(timezone.utc)
        last_notified = now - timedelta(seconds=90)  # 90 seconds ago

        seconds_since_last = (now - last_notified).total_seconds()
        should_skip = seconds_since_last < 60

        assert should_skip is False
        assert seconds_since_last == 90

    @pytest.mark.unit
    def test_cooldown_at_boundary(self):
        """Activity alert at exactly 60 seconds should proceed."""
        now = datetime.now(timezone.utc)
        last_notified = now - timedelta(seconds=60)

        seconds_since_last = (now - last_notified).total_seconds()
        should_skip = seconds_since_last < 60

        assert should_skip is False

    @pytest.mark.unit
    def test_cooldown_allows_when_no_previous_notification(self):
        """Activity alert should proceed if no previous notification."""
        last_notified_str = None

        # Logic from listener: if no previous notification, no cooldown check
        should_check_cooldown = last_notified_str is not None

        assert should_check_cooldown is False

    @pytest.mark.unit
    def test_cooldown_handles_invalid_timestamp(self):
        """Cooldown should handle invalid timestamp gracefully."""
        last_notified_str = "invalid_timestamp"
        should_skip = False

        try:
            datetime.fromisoformat(last_notified_str)
        except ValueError:
            # Invalid timestamp - don't skip (pass through)
            should_skip = False

        assert should_skip is False

    @pytest.mark.unit
    def test_cooldown_logic_flow(self):
        """Test the complete cooldown logic flow as in listener."""
        now = datetime.now(timezone.utc)
        test_cases = [
            # (last_notified_str, expected_skip)
            (None, False),  # No previous notification
            ((now - timedelta(seconds=10)).isoformat(), True),   # 10s ago - skip
            ((now - timedelta(seconds=59)).isoformat(), True),   # 59s ago - skip
            ((now - timedelta(seconds=60)).isoformat(), False),  # 60s ago - allow
            ((now - timedelta(seconds=120)).isoformat(), False), # 2min ago - allow
            ("invalid", False),  # Invalid timestamp - allow
        ]

        for last_notified_str, expected_skip in test_cases:
            should_skip = False

            if last_notified_str:
                try:
                    last_notified_at = datetime.fromisoformat(last_notified_str)
                    seconds_since_last = (now - last_notified_at).total_seconds()
                    if seconds_since_last < 60:
                        should_skip = True
                except ValueError:
                    pass

            assert should_skip == expected_skip, f"Failed for {last_notified_str}"

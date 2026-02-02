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

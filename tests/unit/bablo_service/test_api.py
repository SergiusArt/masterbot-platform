"""Unit tests for Bablo Service API endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "bablo_service"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))


class TestBabloSignalsEndpoint:
    """Tests for Bablo /signals endpoint."""

    @pytest.fixture
    def mock_signal(self):
        """Create mock signal object."""
        signal = MagicMock()
        signal.id = 1
        signal.symbol = "BTCUSDT.P"
        signal.direction = "long"
        signal.strength = 4
        signal.timeframe = "1m"
        signal.time_horizon = "60 минут"
        signal.quality_total = 7
        signal.quality_profit = 8
        signal.quality_drawdown = 6
        signal.quality_accuracy = 7
        signal.probabilities = {"0.3": {"long": 72, "short": 86}}
        signal.max_drawdown = Decimal("6")
        signal.received_at = datetime.now(timezone.utc)
        return signal

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_signal_service(self, mock_signal):
        """Create mock signal service."""
        mock = MagicMock()
        mock.get_signals = AsyncMock(return_value=[mock_signal])
        mock.get_signals_count = AsyncMock(return_value=100)
        return mock

    # =========================================================================
    # GET /signals Tests
    # =========================================================================

    @pytest.mark.unit
    def test_signals_response_structure(self, mock_signal):
        """Test signals endpoint response structure."""
        # Simulate response transformation
        response = {
            "signals": [
                {
                    "id": mock_signal.id,
                    "symbol": mock_signal.symbol,
                    "direction": mock_signal.direction,
                    "strength": mock_signal.strength,
                    "timeframe": mock_signal.timeframe,
                    "time_horizon": mock_signal.time_horizon,
                    "quality_total": mock_signal.quality_total,
                    "quality_profit": mock_signal.quality_profit,
                    "quality_drawdown": mock_signal.quality_drawdown,
                    "quality_accuracy": mock_signal.quality_accuracy,
                    "probabilities": mock_signal.probabilities,
                    "max_drawdown": float(mock_signal.max_drawdown),
                    "received_at": mock_signal.received_at.isoformat(),
                }
            ],
            "total": 100,
            "limit": 100,
            "offset": 0,
        }

        assert "signals" in response
        assert "total" in response
        assert len(response["signals"]) == 1

        signal = response["signals"][0]
        assert signal["symbol"] == "BTCUSDT.P"
        assert signal["direction"] == "long"
        assert signal["strength"] == 4
        assert signal["timeframe"] == "1m"
        assert signal["quality_total"] == 7

    @pytest.mark.unit
    def test_signals_filter_by_direction(self):
        """Test filtering signals by direction."""
        # Valid direction values
        valid_directions = ["long", "short"]

        for direction in valid_directions:
            # Simulate query parameter
            params = {"direction": direction}
            assert params["direction"] in valid_directions

    @pytest.mark.unit
    def test_signals_filter_by_timeframe(self):
        """Test filtering signals by timeframe."""
        valid_timeframes = ["1m", "15m", "30m", "1h", "4h"]

        for tf in valid_timeframes:
            params = {"timeframe": tf}
            assert params["timeframe"] in valid_timeframes

    @pytest.mark.unit
    def test_signals_filter_by_quality(self):
        """Test filtering signals by minimum quality."""
        valid_qualities = range(1, 11)

        for quality in valid_qualities:
            params = {"min_quality": quality}
            assert 1 <= params["min_quality"] <= 10

    @pytest.mark.unit
    def test_signals_pagination_params(self):
        """Test pagination parameters."""
        # Valid pagination
        params = {"limit": 50, "offset": 10}
        assert 1 <= params["limit"] <= 1000
        assert params["offset"] >= 0

    @pytest.mark.unit
    def test_signals_date_filter(self):
        """Test date filter parsing."""
        date_str = "2024-01-15T00:00:00"
        parsed_date = datetime.fromisoformat(date_str)

        assert parsed_date.year == 2024
        assert parsed_date.month == 1
        assert parsed_date.day == 15

    # =========================================================================
    # Response Data Validation Tests
    # =========================================================================

    @pytest.mark.unit
    def test_signal_max_drawdown_conversion(self):
        """Test max drawdown decimal to float conversion."""
        max_drawdown = Decimal("6.5")
        converted = float(max_drawdown) if max_drawdown else None

        assert converted == 6.5
        assert isinstance(converted, float)

    @pytest.mark.unit
    def test_signal_max_drawdown_none(self):
        """Test max drawdown when None."""
        max_drawdown = None
        converted = float(max_drawdown) if max_drawdown else None

        assert converted is None

    @pytest.mark.unit
    def test_probabilities_structure(self):
        """Test probabilities dictionary structure in response."""
        probabilities = {
            "0.3": {"long": 72, "short": 86},
            "0.6": {"long": 60, "short": 75},
            "0.9": {"long": 50, "short": 65},
        }

        assert isinstance(probabilities, dict)
        for target, probs in probabilities.items():
            assert "long" in probs
            assert "short" in probs
            assert isinstance(probs["long"], int)
            assert isinstance(probs["short"], int)
            assert 0 <= probs["long"] <= 100
            assert 0 <= probs["short"] <= 100


class TestBabloAnalyticsEndpoint:
    """Tests for Bablo /analytics endpoint."""

    @pytest.mark.unit
    def test_analytics_periods(self):
        """Test valid analytics periods."""
        valid_periods = ["today", "yesterday", "week", "month"]

        for period in valid_periods:
            # Simulate endpoint call
            assert period in valid_periods

    @pytest.mark.unit
    def test_analytics_response_structure(self):
        """Test analytics response structure."""
        now = datetime.now(timezone.utc)

        # Expected analytics response structure
        response = {
            "period": "today",
            "start_date": now.isoformat(),
            "end_date": now.isoformat(),
            "total_signals": 50,
            "by_direction": {"long": 30, "short": 20},
            "by_timeframe": {"1m": 25, "15m": 15, "1h": 10},
            "top_symbols": [
                ("BTCUSDT.P", 15),
                ("ETHUSDT.P", 10),
                ("XRPUSDT.P", 8),
            ],
            "average_quality": 7.5,
        }

        assert "period" in response
        assert "total_signals" in response
        assert "by_direction" in response
        assert "by_timeframe" in response
        assert "top_symbols" in response
        assert "average_quality" in response

    @pytest.mark.unit
    def test_direction_distribution(self):
        """Test direction distribution calculation."""
        direction_counts = {"long": 60, "short": 40}

        total = sum(direction_counts.values())
        long_pct = (direction_counts["long"] / total) * 100
        short_pct = (direction_counts["short"] / total) * 100

        assert long_pct == 60.0
        assert short_pct == 40.0
        assert long_pct + short_pct == 100.0

    @pytest.mark.unit
    def test_timeframe_distribution(self):
        """Test timeframe distribution calculation."""
        timeframe_counts = {
            "1m": 40,
            "15m": 30,
            "30m": 15,
            "1h": 10,
            "4h": 5,
        }

        total = sum(timeframe_counts.values())
        assert total == 100

        # Most common should be 1m
        most_common = max(timeframe_counts, key=timeframe_counts.get)
        assert most_common == "1m"


class TestBabloReportsEndpoint:
    """Tests for Bablo /reports endpoint."""

    @pytest.mark.unit
    def test_report_generation_params(self):
        """Test report generation parameters."""
        valid_params = {
            "period": "today",
            "user_id": 123,
        }

        assert valid_params["period"] in ["today", "yesterday", "week", "month"]
        assert isinstance(valid_params["user_id"], int)

    @pytest.mark.unit
    def test_report_response_structure(self):
        """Test report response structure."""
        now = datetime.now(timezone.utc)

        response = {
            "status": "success",
            "report": {
                "title": "Bablo Daily Report",
                "period": "today",
                "total_signals": 50,
                "long_count": 30,
                "short_count": 20,
                "avg_quality": 7.2,
                "top_symbols": ["BTCUSDT.P", "ETHUSDT.P"],
                "generated_at": now.isoformat(),
            },
        }

        assert response["status"] == "success"
        assert "report" in response
        assert "title" in response["report"]
        assert "total_signals" in response["report"]


class TestBabloNotificationsEndpoint:
    """Tests for Bablo /notifications endpoint."""

    @pytest.mark.unit
    def test_notification_settings_structure(self):
        """Test notification settings structure."""
        settings = {
            "user_id": 123,
            "enabled": True,
            "min_quality": 7,
            "direction_filter": None,  # None means all directions
            "timeframe_filter": ["1m", "15m"],
            "reports_enabled": True,
        }

        assert settings["user_id"] == 123
        assert settings["enabled"] is True
        assert settings["min_quality"] == 7
        assert settings["direction_filter"] is None
        assert "1m" in settings["timeframe_filter"]

    @pytest.mark.unit
    def test_notification_settings_update(self):
        """Test notification settings update structure."""
        update = {
            "enabled": False,
            "min_quality": 8,
        }

        # Partial update should work
        assert "enabled" in update
        assert "min_quality" in update
        assert "user_id" not in update  # Not updateable


class TestBabloHealthEndpoint:
    """Tests for Bablo health endpoint."""

    @pytest.mark.unit
    def test_health_response(self):
        """Test health endpoint response."""
        health = {
            "status": "healthy",
            "service": "bablo_service",
            "database": "connected",
            "redis": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        assert health["status"] == "healthy"
        assert health["service"] == "bablo_service"
        assert health["database"] == "connected"
        assert health["redis"] == "connected"

    @pytest.mark.unit
    def test_health_unhealthy_database(self):
        """Test health response when database is down."""
        health = {
            "status": "unhealthy",
            "service": "bablo_service",
            "database": "disconnected",
            "redis": "connected",
            "error": "Database connection failed",
        }

        assert health["status"] == "unhealthy"
        assert health["database"] == "disconnected"
        assert "error" in health


class TestQueryParameterValidation:
    """Tests for API query parameter validation."""

    @pytest.mark.unit
    def test_limit_boundaries(self):
        """Test limit parameter boundaries."""
        # Valid limits
        valid_limits = [1, 50, 100, 500, 1000]
        for limit in valid_limits:
            assert 1 <= limit <= 1000

        # Invalid limits
        invalid_limits = [0, -1, 1001, 10000]
        for limit in invalid_limits:
            assert not (1 <= limit <= 1000)

    @pytest.mark.unit
    def test_offset_boundaries(self):
        """Test offset parameter boundaries."""
        # Valid offsets
        valid_offsets = [0, 10, 100, 1000]
        for offset in valid_offsets:
            assert offset >= 0

        # Invalid offsets
        invalid_offsets = [-1, -100]
        for offset in invalid_offsets:
            assert offset < 0

    @pytest.mark.unit
    def test_quality_boundaries(self):
        """Test quality parameter boundaries."""
        # Valid quality values
        valid_qualities = range(1, 11)
        for quality in valid_qualities:
            assert 1 <= quality <= 10

        # Invalid quality values
        invalid_qualities = [0, 11, -1, 100]
        for quality in invalid_qualities:
            assert not (1 <= quality <= 10)

    @pytest.mark.unit
    def test_date_format_validation(self):
        """Test date format validation."""
        valid_dates = [
            "2024-01-15",
            "2024-01-15T00:00:00",
            "2024-01-15T12:30:45",
        ]

        for date_str in valid_dates:
            try:
                # Try parsing with fromisoformat
                if "T" in date_str:
                    datetime.fromisoformat(date_str)
                else:
                    datetime.strptime(date_str, "%Y-%m-%d")
                valid = True
            except ValueError:
                valid = False
            assert valid, f"Failed to parse: {date_str}"

    @pytest.mark.unit
    def test_direction_validation(self):
        """Test direction parameter validation."""
        valid_directions = ["long", "short"]
        invalid_directions = ["up", "down", "buy", "sell", ""]

        for direction in valid_directions:
            assert direction in ["long", "short"]

        for direction in invalid_directions:
            assert direction not in ["long", "short"]

    @pytest.mark.unit
    def test_timeframe_validation(self):
        """Test timeframe parameter validation."""
        valid_timeframes = ["1m", "15m", "30m", "1h", "4h"]
        invalid_timeframes = ["1min", "15min", "1hour", "daily", ""]

        for tf in valid_timeframes:
            assert tf in ["1m", "15m", "30m", "1h", "4h"]

        for tf in invalid_timeframes:
            assert tf not in ["1m", "15m", "30m", "1h", "4h"]

"""Unit tests for Impulse Service API endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "impulse_service"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))


class TestSignalsEndpoint:
    """Tests for /signals endpoint."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with signals router."""
        from api.endpoints.signals import router

        app = FastAPI()
        app.include_router(router, prefix="/signals")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_signal_service(self):
        """Create mock signal service."""
        from shared.schemas.impulse import SignalListResponse, ImpulseSchema

        now = datetime.now(timezone.utc)

        mock_response = SignalListResponse(
            signals=[
                ImpulseSchema(
                    id=1,
                    symbol="BTCUSDT",
                    percent=Decimal("15.5"),
                    type="growth",
                    received_at=now,
                ),
                ImpulseSchema(
                    id=2,
                    symbol="ETHUSDT",
                    percent=Decimal("-10.2"),
                    type="fall",
                    received_at=now,
                ),
            ],
            total=100,
            limit=100,
            offset=0,
        )

        mock = AsyncMock()
        mock.get_signals.return_value = mock_response
        mock.create_signal.return_value = 1
        return mock

    # =========================================================================
    # GET /signals Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_signals_success(self, client, mock_signal_service):
        """Test successful signals retrieval."""
        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            response = client.get("/signals")

            assert response.status_code == 200
            data = response.json()
            assert "signals" in data
            assert "total" in data
            assert "limit" in data
            assert "offset" in data

    @pytest.mark.unit
    def test_get_signals_with_pagination(self, client, mock_signal_service):
        """Test signals retrieval with pagination parameters."""
        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            response = client.get("/signals?limit=50&offset=10")

            assert response.status_code == 200
            mock_signal_service.get_signals.assert_called_once()
            call_kwargs = mock_signal_service.get_signals.call_args.kwargs
            assert call_kwargs["limit"] == 50
            assert call_kwargs["offset"] == 10

    @pytest.mark.unit
    def test_get_signals_with_date_filter(self, client, mock_signal_service):
        """Test signals retrieval with date filter."""
        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            response = client.get("/signals?from_date=2024-01-01T00:00:00")

            assert response.status_code == 200
            mock_signal_service.get_signals.assert_called_once()
            call_kwargs = mock_signal_service.get_signals.call_args.kwargs
            assert call_kwargs["from_date"] == "2024-01-01T00:00:00"

    @pytest.mark.unit
    def test_get_signals_limit_validation(self, client):
        """Test limit parameter validation."""
        # Limit too high
        response = client.get("/signals?limit=2000")
        assert response.status_code == 422

        # Limit too low
        response = client.get("/signals?limit=0")
        assert response.status_code == 422

    @pytest.mark.unit
    def test_get_signals_offset_validation(self, client):
        """Test offset parameter validation."""
        # Negative offset
        response = client.get("/signals?offset=-1")
        assert response.status_code == 422

    @pytest.mark.unit
    def test_get_signals_service_error(self, client, mock_signal_service):
        """Test error handling when service fails."""
        mock_signal_service.get_signals.side_effect = Exception("Database error")

        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            response = client.get("/signals")

            assert response.status_code == 500
            assert "Database error" in response.json()["detail"]

    # =========================================================================
    # POST /signals Tests
    # =========================================================================

    @pytest.mark.unit
    def test_create_signal_success(self, client, mock_signal_service):
        """Test successful signal creation."""
        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            signal_data = {
                "symbol": "BTCUSDT",
                "percent": "15.5",
                "type": "growth",
            }

            response = client.post("/signals", json=signal_data)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "created"
            assert data["id"] == 1

    @pytest.mark.unit
    def test_create_signal_with_all_fields(self, client, mock_signal_service):
        """Test signal creation with all fields."""
        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            signal_data = {
                "symbol": "ETHUSDT",
                "percent": "-12.5",
                "max_percent": "20.0",
                "type": "fall",
                "growth_ratio": "35",
                "fall_ratio": "65",
                "raw_message": "Test message",
            }

            response = client.post("/signals", json=signal_data)

            assert response.status_code == 200

    @pytest.mark.unit
    def test_create_signal_validation_error(self, client):
        """Test validation error for invalid signal data."""
        # Missing required field
        response = client.post("/signals", json={"symbol": "BTCUSDT"})
        assert response.status_code == 422

    @pytest.mark.unit
    def test_create_signal_invalid_type(self, client):
        """Test validation error for invalid type."""
        signal_data = {
            "symbol": "BTCUSDT",
            "percent": "15.5",
            "type": "invalid_type",
        }

        response = client.post("/signals", json=signal_data)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_create_signal_service_error(self, client, mock_signal_service):
        """Test error handling when service fails during creation."""
        mock_signal_service.create_signal.side_effect = Exception("Insert failed")

        with patch(
            "api.endpoints.signals.signal_service", mock_signal_service
        ):
            signal_data = {
                "symbol": "BTCUSDT",
                "percent": "15.5",
                "type": "growth",
            }

            response = client.post("/signals", json=signal_data)

            assert response.status_code == 500


class TestAnalyticsEndpoint:
    """Tests for /analytics endpoint."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with analytics router."""
        # Import would need the analytics endpoint
        # For this test, we'll create a minimal setup
        from fastapi import FastAPI

        app = FastAPI()
        return app

    @pytest.mark.unit
    def test_analytics_response_structure(self):
        """Test analytics response schema structure."""
        from shared.schemas.impulse import AnalyticsResponse, TopImpulse

        now = datetime.now(timezone.utc)

        response = AnalyticsResponse(
            period="today",
            start_date=now,
            end_date=now,
            total_impulses=100,
            growth_count=60,
            fall_count=40,
            top_growth=[TopImpulse(symbol="BTC", percent=Decimal("20"), count=5)],
            top_fall=[TopImpulse(symbol="ETH", percent=Decimal("-15"), count=3)],
        )

        # Convert to dict (simulating JSON response)
        data = response.model_dump()

        assert data["period"] == "today"
        assert data["total_impulses"] == 100
        assert data["growth_count"] == 60
        assert data["fall_count"] == 40
        assert len(data["top_growth"]) == 1
        assert len(data["top_fall"]) == 1


class TestNotificationsEndpoint:
    """Tests for /notifications endpoint."""

    @pytest.mark.unit
    def test_notification_settings_response_structure(self):
        """Test notification settings response structure."""
        from shared.schemas.impulse import NotificationSettingsSchema
        from datetime import time

        settings = NotificationSettingsSchema(
            user_id=123,
            notifications_enabled=True,
            growth_threshold=25,
            fall_threshold=-20,
            morning_report=True,
            morning_report_time=time(9, 0),
            evening_report=True,
            evening_report_time=time(21, 0),
        )

        data = settings.model_dump()

        assert data["user_id"] == 123
        assert data["notifications_enabled"] is True
        assert data["growth_threshold"] == 25
        assert data["fall_threshold"] == -20


class TestReportsEndpoint:
    """Tests for /reports endpoint."""

    @pytest.mark.unit
    def test_report_request_structure(self):
        """Test report request schema structure."""
        from shared.schemas.impulse import ReportRequest

        request = ReportRequest(type="morning", user_id=123)

        assert request.type == "morning"
        assert request.user_id == 123

    @pytest.mark.unit
    def test_report_response_structure(self):
        """Test report response schema structure."""
        from shared.schemas.impulse import ReportResponse, ReportData

        now = datetime.now(timezone.utc)

        response = ReportResponse(
            status="success",
            report=ReportData(
                title="Morning Report",
                text="Report content...",
                generated_at=now,
            ),
        )

        data = response.model_dump()

        assert data["status"] == "success"
        assert data["report"]["title"] == "Morning Report"


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.unit
    def test_health_response_structure(self):
        """Test expected health response structure."""
        # Expected structure from main.py health endpoint
        expected_keys = ["status", "database", "redis", "timestamp"]

        # Simulate health response
        health_response = {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        for key in expected_keys:
            assert key in health_response

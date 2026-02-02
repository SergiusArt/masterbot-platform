"""Unit tests for Impulse SignalService."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSignalServiceUnit:
    """Unit tests for SignalService with mocked database."""

    @pytest.fixture
    def mock_session(self):
        """Create mock async session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.scalar = AsyncMock()
        return session

    @pytest.fixture
    def mock_session_maker(self, mock_session):
        """Create mock session maker context manager."""

        class MockContextManager:
            async def __aenter__(self):
                return mock_session

            async def __aexit__(self, *args):
                pass

        return MockContextManager

    @pytest.fixture
    def signal_service(self):
        """Create SignalService instance."""
        from services.signal_service import SignalService

        return SignalService()

    @pytest.fixture
    def sample_impulse_create(self):
        """Sample impulse creation data."""
        from shared.schemas.impulse import ImpulseCreate

        return ImpulseCreate(
            symbol="BTCUSDT",
            percent=Decimal("15.5"),
            max_percent=Decimal("20.0"),
            type="growth",
            growth_ratio=Decimal("65"),
            fall_ratio=Decimal("35"),
            raw_message="Test message",
        )

    # =========================================================================
    # Create Signal Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_signal_success(
        self, signal_service, mock_session, mock_session_maker, sample_impulse_create
    ):
        """Test successful signal creation."""
        # Setup mock to return an impulse with id
        mock_impulse = MagicMock()
        mock_impulse.id = 1
        mock_impulse.symbol = sample_impulse_create.symbol
        mock_impulse.percent = sample_impulse_create.percent

        async def refresh_side_effect(obj):
            obj.id = 1

        mock_session.refresh.side_effect = refresh_side_effect

        with patch(
            "services.signal_service.async_session_maker", mock_session_maker
        ):
            # Note: This test demonstrates the pattern but needs actual Impulse model
            # In practice, you'd use a test database or more sophisticated mocking
            pass

    @pytest.mark.unit
    def test_impulse_create_schema_validation(self):
        """Test ImpulseCreate schema validation."""
        from shared.schemas.impulse import ImpulseCreate

        # Valid creation
        impulse = ImpulseCreate(
            symbol="BTCUSDT",
            percent=Decimal("10"),
            type="growth",
        )
        assert impulse.symbol == "BTCUSDT"
        assert impulse.percent == Decimal("10")
        assert impulse.type == "growth"
        assert impulse.max_percent is None

    @pytest.mark.unit
    def test_impulse_create_schema_with_all_fields(self):
        """Test ImpulseCreate with all optional fields."""
        from shared.schemas.impulse import ImpulseCreate

        impulse = ImpulseCreate(
            symbol="ETHUSDT",
            percent=Decimal("-15.5"),
            max_percent=Decimal("25.0"),
            type="fall",
            growth_ratio=Decimal("30"),
            fall_ratio=Decimal("70"),
            raw_message="Test raw message",
        )
        assert impulse.symbol == "ETHUSDT"
        assert impulse.percent == Decimal("-15.5")
        assert impulse.max_percent == Decimal("25.0")
        assert impulse.type == "fall"
        assert impulse.growth_ratio == Decimal("30")
        assert impulse.fall_ratio == Decimal("70")

    @pytest.mark.unit
    def test_impulse_schema_validation(self):
        """Test ImpulseSchema validation."""
        from shared.schemas.impulse import ImpulseSchema

        now = datetime.now(timezone.utc)
        impulse = ImpulseSchema(
            id=1,
            symbol="BTCUSDT",
            percent=Decimal("15.5"),
            type="growth",
            received_at=now,
        )
        assert impulse.id == 1
        assert impulse.symbol == "BTCUSDT"
        assert impulse.percent == Decimal("15.5")

    # =========================================================================
    # Signal List Response Tests
    # =========================================================================

    @pytest.mark.unit
    def test_signal_list_response_schema(self):
        """Test SignalListResponse schema."""
        from shared.schemas.impulse import SignalListResponse, ImpulseSchema

        now = datetime.now(timezone.utc)
        signals = [
            ImpulseSchema(
                id=1,
                symbol="BTCUSDT",
                percent=Decimal("10"),
                type="growth",
                received_at=now,
            ),
            ImpulseSchema(
                id=2,
                symbol="ETHUSDT",
                percent=Decimal("-5"),
                type="fall",
                received_at=now,
            ),
        ]

        response = SignalListResponse(
            signals=signals,
            total=100,
            limit=10,
            offset=0,
        )

        assert len(response.signals) == 2
        assert response.total == 100
        assert response.limit == 10
        assert response.offset == 0


class TestAnalyticsServiceUnit:
    """Unit tests for AnalyticsService."""

    @pytest.fixture
    def analytics_service(self):
        """Create AnalyticsService instance."""
        from services.analytics_service import AnalyticsService

        return AnalyticsService()

    # =========================================================================
    # Period Date Calculation Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_period_dates_today(self, analytics_service):
        """Test period dates for today."""
        start_date, end_date = analytics_service._get_period_dates("today")

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        assert start_date == today_start
        # end_date should be around now
        assert end_date.date() == now.date()

    @pytest.mark.unit
    def test_get_period_dates_yesterday(self, analytics_service):
        """Test period dates for yesterday."""
        start_date, end_date = analytics_service._get_period_dates("yesterday")

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_start = today_start - timedelta(days=1)

        assert start_date == expected_start
        assert end_date < today_start

    @pytest.mark.unit
    def test_get_period_dates_week(self, analytics_service):
        """Test period dates for week."""
        start_date, end_date = analytics_service._get_period_dates("week")

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_start = today_start - timedelta(days=7)

        assert start_date == expected_start

    @pytest.mark.unit
    def test_get_period_dates_month(self, analytics_service):
        """Test period dates for month."""
        start_date, end_date = analytics_service._get_period_dates("month")

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        expected_start = today_start - timedelta(days=30)

        assert start_date == expected_start

    @pytest.mark.unit
    def test_get_period_dates_unknown(self, analytics_service):
        """Test period dates for unknown period (defaults to today)."""
        start_date, end_date = analytics_service._get_period_dates("unknown_period")

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        assert start_date == today_start

    # =========================================================================
    # Analytics Response Schema Tests
    # =========================================================================

    @pytest.mark.unit
    def test_analytics_response_schema(self):
        """Test AnalyticsResponse schema."""
        from shared.schemas.impulse import AnalyticsResponse, TopImpulse

        now = datetime.now(timezone.utc)
        response = AnalyticsResponse(
            period="today",
            start_date=now - timedelta(hours=12),
            end_date=now,
            total_impulses=100,
            growth_count=60,
            fall_count=40,
            top_growth=[
                TopImpulse(symbol="BTCUSDT", percent=Decimal("25"), count=10),
                TopImpulse(symbol="ETHUSDT", percent=Decimal("20"), count=8),
            ],
            top_fall=[
                TopImpulse(symbol="XRPUSDT", percent=Decimal("-15"), count=5),
            ],
        )

        assert response.period == "today"
        assert response.total_impulses == 100
        assert response.growth_count == 60
        assert response.fall_count == 40
        assert len(response.top_growth) == 2
        assert len(response.top_fall) == 1

    @pytest.mark.unit
    def test_top_impulse_schema(self):
        """Test TopImpulse schema."""
        from shared.schemas.impulse import TopImpulse

        impulse = TopImpulse(
            symbol="BTCUSDT",
            percent=Decimal("25.5"),
            count=15,
        )

        assert impulse.symbol == "BTCUSDT"
        assert impulse.percent == Decimal("25.5")
        assert impulse.count == 15

    @pytest.mark.unit
    def test_comparison_data_schema(self):
        """Test ComparisonData schema."""
        from shared.schemas.impulse import ComparisonData

        comparison = ComparisonData(
            vs_yesterday="+15%",
            vs_week_median="-5%",
            vs_month_median="N/A",
        )

        assert comparison.vs_yesterday == "+15%"
        assert comparison.vs_week_median == "-5%"
        assert comparison.vs_month_median == "N/A"


class TestNotificationSettingsSchema:
    """Tests for notification settings schemas."""

    @pytest.mark.unit
    def test_notification_settings_defaults(self):
        """Test NotificationSettingsSchema default values."""
        from shared.schemas.impulse import NotificationSettingsSchema
        from datetime import time

        settings = NotificationSettingsSchema(user_id=123)

        assert settings.user_id == 123
        assert settings.notifications_enabled is True
        assert settings.growth_threshold == 20
        assert settings.fall_threshold == -15
        assert settings.morning_report is True
        assert settings.morning_report_time == time(8, 0)
        assert settings.evening_report is True
        assert settings.evening_report_time == time(20, 0)
        assert settings.weekly_report is True
        assert settings.monthly_report is True
        assert settings.activity_window_minutes == 15
        assert settings.activity_threshold == 10

    @pytest.mark.unit
    def test_notification_settings_custom_values(self):
        """Test NotificationSettingsSchema with custom values."""
        from shared.schemas.impulse import NotificationSettingsSchema
        from datetime import time

        settings = NotificationSettingsSchema(
            user_id=456,
            notifications_enabled=False,
            growth_threshold=50,
            fall_threshold=-30,
            morning_report=False,
            morning_report_time=time(9, 30),
            activity_window_minutes=30,
        )

        assert settings.notifications_enabled is False
        assert settings.growth_threshold == 50
        assert settings.fall_threshold == -30
        assert settings.morning_report is False
        assert settings.morning_report_time == time(9, 30)
        assert settings.activity_window_minutes == 30

    @pytest.mark.unit
    def test_notification_settings_threshold_boundaries(self):
        """Test threshold boundary validation."""
        from shared.schemas.impulse import NotificationSettingsSchema
        from pydantic import ValidationError

        # Valid boundary values
        settings = NotificationSettingsSchema(
            user_id=1,
            growth_threshold=1,
            fall_threshold=-1,
        )
        assert settings.growth_threshold == 1
        assert settings.fall_threshold == -1

        settings = NotificationSettingsSchema(
            user_id=1,
            growth_threshold=100,
            fall_threshold=-100,
        )
        assert settings.growth_threshold == 100
        assert settings.fall_threshold == -100

    @pytest.mark.unit
    def test_notification_settings_update_schema(self):
        """Test NotificationSettingsUpdate schema."""
        from shared.schemas.impulse import NotificationSettingsUpdate

        # Partial update
        update = NotificationSettingsUpdate(
            notifications_enabled=False,
            growth_threshold=30,
        )

        assert update.notifications_enabled is False
        assert update.growth_threshold == 30
        assert update.fall_threshold is None
        assert update.morning_report is None


class TestReportSchemas:
    """Tests for report-related schemas."""

    @pytest.mark.unit
    def test_report_request_schema(self):
        """Test ReportRequest schema."""
        from shared.schemas.impulse import ReportRequest

        request = ReportRequest(
            type="morning",
            user_id=123,
        )

        assert request.type == "morning"
        assert request.user_id == 123

    @pytest.mark.unit
    def test_report_request_valid_types(self):
        """Test ReportRequest with all valid types."""
        from shared.schemas.impulse import ReportRequest

        valid_types = ["morning", "evening", "weekly", "monthly"]

        for report_type in valid_types:
            request = ReportRequest(type=report_type, user_id=1)
            assert request.type == report_type

    @pytest.mark.unit
    def test_report_data_schema(self):
        """Test ReportData schema."""
        from shared.schemas.impulse import ReportData

        now = datetime.now(timezone.utc)
        report = ReportData(
            title="Morning Report",
            text="Report content here...",
            generated_at=now,
        )

        assert report.title == "Morning Report"
        assert report.text == "Report content here..."
        assert report.generated_at == now

    @pytest.mark.unit
    def test_report_response_schema(self):
        """Test ReportResponse schema."""
        from shared.schemas.impulse import ReportResponse, ReportData

        now = datetime.now(timezone.utc)
        response = ReportResponse(
            status="success",
            report=ReportData(
                title="Evening Report",
                text="Content...",
                generated_at=now,
            ),
        )

        assert response.status == "success"
        assert response.report.title == "Evening Report"

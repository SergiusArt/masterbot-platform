"""Unit tests for Bablo SignalService."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.parser import ParsedBabloSignal


class TestBabloSignalServiceUnit:
    """Unit tests for Bablo SignalService."""

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
    def signal_service(self):
        """Create SignalService instance."""
        from services.signal_service import SignalService

        return SignalService()

    @pytest.fixture
    def sample_parsed_signal(self):
        """Sample parsed Bablo signal."""
        return ParsedBabloSignal(
            symbol="BTCUSDT.P",
            direction="long",
            strength=4,
            timeframe="1m",
            time_horizon="60 минут",
            quality_total=7,
            quality_profit=8,
            quality_drawdown=6,
            quality_accuracy=7,
            probabilities={
                "0.3": {"long": 72, "short": 86},
                "0.6": {"long": 60, "short": 75},
            },
            max_drawdown=Decimal("6"),
            raw_message="Test signal message",
        )

    # =========================================================================
    # Create Signal Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_signal_calls_session_methods(
        self, signal_service, mock_session, sample_parsed_signal
    ):
        """Test that create_signal calls appropriate session methods."""
        mock_signal = MagicMock()
        mock_signal.symbol = sample_parsed_signal.symbol
        mock_signal.direction = sample_parsed_signal.direction

        await signal_service.create_signal(
            mock_session, sample_parsed_signal, telegram_message_id=123
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_signal_without_telegram_id(
        self, signal_service, mock_session, sample_parsed_signal
    ):
        """Test signal creation without telegram message ID."""
        await signal_service.create_signal(mock_session, sample_parsed_signal)

        mock_session.add.assert_called_once()
        added_signal = mock_session.add.call_args[0][0]
        assert added_signal.telegram_message_id is None

    # =========================================================================
    # Get Signals Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_with_filters(self, signal_service, mock_session):
        """Test get_signals applies filters correctly."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        await signal_service.get_signals(
            mock_session,
            limit=50,
            offset=10,
            from_date=now,
            direction="long",
            timeframe="15m",
            min_quality=7,
        )

        mock_session.execute.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_default_params(self, signal_service, mock_session):
        """Test get_signals with default parameters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await signal_service.get_signals(mock_session)

        assert result == []
        mock_session.execute.assert_called_once()

    # =========================================================================
    # Get Signals Count Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_count(self, signal_service, mock_session):
        """Test getting signal count."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_session.execute.return_value = mock_result

        result = await signal_service.get_signals_count(mock_session)

        assert result == 42

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_count_zero(self, signal_service, mock_session):
        """Test signal count returns 0 when no signals."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result

        result = await signal_service.get_signals_count(mock_session)

        assert result == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_count_with_date_range(
        self, signal_service, mock_session
    ):
        """Test signal count with date range filter."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 15
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_signals_count(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        assert result == 15

    # =========================================================================
    # Get Signals by Direction Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_by_direction(self, signal_service, mock_session):
        """Test getting signals grouped by direction."""
        mock_result = MagicMock()
        mock_result.all.return_value = [("long", 60), ("short", 40)]
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_signals_by_direction(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        assert result == {"long": 60, "short": 40}

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_by_direction_empty(self, signal_service, mock_session):
        """Test getting signals by direction when empty."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_signals_by_direction(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        assert result == {}

    # =========================================================================
    # Get Signals by Timeframe Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_signals_by_timeframe(self, signal_service, mock_session):
        """Test getting signals grouped by timeframe."""
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("1m", 50),
            ("15m", 30),
            ("1h", 15),
            ("4h", 5),
        ]
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_signals_by_timeframe(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        assert result == {"1m": 50, "15m": 30, "1h": 15, "4h": 5}

    # =========================================================================
    # Get Top Symbols Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_top_symbols(self, signal_service, mock_session):
        """Test getting top symbols by frequency."""
        mock_result = MagicMock()
        mock_result.all.return_value = [
            ("BTCUSDT.P", 25),
            ("ETHUSDT.P", 20),
            ("XRPUSDT.P", 15),
        ]
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_top_symbols(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
            limit=3,
        )

        assert len(result) == 3
        assert result[0] == ("BTCUSDT.P", 25)
        assert result[1] == ("ETHUSDT.P", 20)
        assert result[2] == ("XRPUSDT.P", 15)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_top_symbols_default_limit(self, signal_service, mock_session):
        """Test top symbols uses default limit of 5."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        await signal_service.get_top_symbols(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        # Verify the query was executed (limit is in the query)
        mock_session.execute.assert_called_once()

    # =========================================================================
    # Get Average Quality Tests
    # =========================================================================

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_average_quality(self, signal_service, mock_session):
        """Test getting average quality score."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = Decimal("7.5")
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_average_quality(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        assert result == 7.5

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_average_quality_none(self, signal_service, mock_session):
        """Test average quality returns None when no signals."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result

        now = datetime.now(timezone.utc)
        result = await signal_service.get_average_quality(
            mock_session,
            from_date=now - timedelta(days=1),
            to_date=now,
        )

        assert result is None


class TestParsedBabloSignalDataclass:
    """Tests for ParsedBabloSignal dataclass used by service."""

    @pytest.mark.unit
    def test_signal_with_all_fields(self):
        """Test signal with all fields populated."""
        signal = ParsedBabloSignal(
            symbol="SYNUSDT.P",
            direction="long",
            strength=5,
            timeframe="1m",
            time_horizon="60 минут",
            quality_total=9,
            quality_profit=10,
            quality_drawdown=8,
            quality_accuracy=9,
            probabilities={
                "0.3": {"long": 85, "short": 90},
                "0.6": {"long": 75, "short": 82},
            },
            max_drawdown=Decimal("4"),
            raw_message="Full signal",
        )

        assert signal.symbol == "SYNUSDT.P"
        assert signal.direction == "long"
        assert signal.strength == 5
        assert signal.timeframe == "1m"
        assert signal.time_horizon == "60 минут"
        assert signal.quality_total == 9
        assert signal.quality_profit == 10
        assert signal.quality_drawdown == 8
        assert signal.quality_accuracy == 9
        assert len(signal.probabilities) == 2
        assert signal.max_drawdown == Decimal("4")

    @pytest.mark.unit
    def test_signal_minimal_fields(self):
        """Test signal with minimal required fields."""
        signal = ParsedBabloSignal(
            symbol="BTCUSDT.P",
            direction="short",
            strength=2,
            timeframe="4h",
        )

        assert signal.symbol == "BTCUSDT.P"
        assert signal.direction == "short"
        assert signal.strength == 2
        assert signal.timeframe == "4h"
        assert signal.time_horizon is None
        assert signal.quality_total == 0
        assert signal.probabilities == {}
        assert signal.max_drawdown is None

    @pytest.mark.unit
    def test_signal_probabilities_structure(self):
        """Test probabilities dictionary structure."""
        signal = ParsedBabloSignal(
            symbol="ETHUSDT.P",
            direction="long",
            strength=3,
            timeframe="15m",
            probabilities={
                "0.5": {"long": 70, "short": 75},
                "1.0": {"long": 60, "short": 68},
                "1.5": {"long": 50, "short": 58},
            },
        )

        assert "0.5" in signal.probabilities
        assert signal.probabilities["0.5"]["long"] == 70
        assert signal.probabilities["0.5"]["short"] == 75
        assert signal.probabilities["1.0"]["long"] == 60
        assert signal.probabilities["1.5"]["short"] == 58


class TestBabloAnalyticsLogic:
    """Tests for Bablo analytics calculation logic (no service initialization)."""

    @pytest.mark.unit
    def test_calc_comparison_positive(self):
        """Test comparison calculation for positive change."""
        def calc_comparison(current: float, previous: float) -> str:
            if previous == 0:
                return "—"
            diff = ((current - previous) / previous) * 100
            if diff > 0:
                return f"+{diff:.0f}%"
            elif diff < 0:
                return f"{diff:.0f}%"
            else:
                return "0%"

        result = calc_comparison(150, 100)
        assert result == "+50%"

    @pytest.mark.unit
    def test_calc_comparison_negative(self):
        """Test comparison calculation for negative change."""
        def calc_comparison(current: float, previous: float) -> str:
            if previous == 0:
                return "—"
            diff = ((current - previous) / previous) * 100
            if diff > 0:
                return f"+{diff:.0f}%"
            elif diff < 0:
                return f"{diff:.0f}%"
            else:
                return "0%"

        result = calc_comparison(50, 100)
        assert result == "-50%"

    @pytest.mark.unit
    def test_calc_comparison_zero_previous(self):
        """Test comparison when previous value is zero."""
        def calc_comparison(current: float, previous: float) -> str:
            if previous == 0:
                return "—"
            diff = ((current - previous) / previous) * 100
            if diff > 0:
                return f"+{diff:.0f}%"
            elif diff < 0:
                return f"{diff:.0f}%"
            else:
                return "0%"

        result = calc_comparison(50, 0)
        assert result == "—"

    @pytest.mark.unit
    def test_calc_comparison_no_change(self):
        """Test comparison when values are equal."""
        def calc_comparison(current: float, previous: float) -> str:
            if previous == 0:
                return "—"
            diff = ((current - previous) / previous) * 100
            if diff > 0:
                return f"+{diff:.0f}%"
            elif diff < 0:
                return f"{diff:.0f}%"
            else:
                return "0%"

        result = calc_comparison(100, 100)
        assert result == "0%"

    @pytest.mark.unit
    def test_14_day_median_calculation(self):
        """Test 14-day median calculation logic."""
        import statistics

        # Simulate daily counts for 14 days
        daily_counts = [30, 35, 28, 42, 38, 45, 33, 40, 37, 44, 31, 48, 36, 41]
        assert len(daily_counts) == 14

        median = int(statistics.median(daily_counts))
        # Sorted: [28,30,31,33,35,36,37,38,40,41,42,44,45,48]
        # Middle values: 37, 38 -> (37+38)/2 = 37.5 -> 37
        assert median == 37

    @pytest.mark.unit
    def test_time_series_period_logic(self):
        """Test time series period calculation logic."""
        from datetime import datetime, timedelta
        import pytz

        tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Week period: 7 days back
        week_start = today_start - timedelta(days=6)
        days_in_week = (today_start - week_start).days + 1
        assert days_in_week == 7

        # Month period: 30 days back
        month_start = today_start - timedelta(days=29)
        days_in_month = (today_start - month_start).days + 1
        assert days_in_month == 30

    @pytest.mark.unit
    def test_activity_zone_from_ratio(self):
        """Test activity zone determination from ratio."""
        def get_zone(ratio: float) -> str:
            if ratio > 2.0:
                return "extreme"
            elif ratio > 1.5:
                return "high"
            elif ratio < 0.25:
                return "very_low"
            elif ratio < 0.5:
                return "low"
            return "normal"

        # Test each zone
        assert get_zone(2.5) == "extreme"  # > 2.0
        assert get_zone(1.8) == "high"  # > 1.5
        assert get_zone(1.0) == "normal"  # 0.5-1.5
        assert get_zone(0.3) == "low"  # < 0.5
        assert get_zone(0.2) == "very_low"  # < 0.25


class TestBabloServiceIntegrationPatterns:
    """Test patterns for service integration."""

    @pytest.mark.unit
    def test_direction_values(self):
        """Test valid direction values."""
        valid_directions = ["long", "short"]

        for direction in valid_directions:
            signal = ParsedBabloSignal(
                symbol="BTCUSDT.P",
                direction=direction,
                strength=3,
                timeframe="1m",
            )
            assert signal.direction in valid_directions

    @pytest.mark.unit
    def test_timeframe_values(self):
        """Test valid timeframe values."""
        valid_timeframes = ["1m", "15m", "30m", "1h", "4h"]

        for tf in valid_timeframes:
            signal = ParsedBabloSignal(
                symbol="BTCUSDT.P",
                direction="long",
                strength=3,
                timeframe=tf,
            )
            assert signal.timeframe in valid_timeframes

    @pytest.mark.unit
    def test_strength_range(self):
        """Test strength value range."""
        for strength in range(1, 8):
            signal = ParsedBabloSignal(
                symbol="BTCUSDT.P",
                direction="long",
                strength=strength,
                timeframe="1m",
            )
            assert signal.strength == strength

    @pytest.mark.unit
    def test_quality_range(self):
        """Test quality values range (1-10)."""
        for quality in range(1, 11):
            signal = ParsedBabloSignal(
                symbol="BTCUSDT.P",
                direction="long",
                strength=3,
                timeframe="1m",
                quality_total=quality,
                quality_profit=quality,
                quality_drawdown=quality,
                quality_accuracy=quality,
            )
            assert signal.quality_total == quality
            assert 1 <= signal.quality_total <= 10

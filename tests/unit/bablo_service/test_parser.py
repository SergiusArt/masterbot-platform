"""Unit tests for BabloParser."""

from decimal import Decimal
from unittest.mock import MagicMock
import sys
import os

import pytest

# Mock the logger before importing parser
sys.modules['shared.utils.logger'] = MagicMock()
sys.modules['shared.utils'] = MagicMock()

# Get the absolute path to bablo_service
BABLO_SERVICE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "bablo_service"))
SHARED_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))

# Remove any conflicting paths and add our paths first
sys.path = [p for p in sys.path if 'impulse_service' not in p]
sys.path.insert(0, BABLO_SERVICE_PATH)
sys.path.insert(0, SHARED_PATH)

from core.parser import BabloParser, ParsedBabloSignal


class TestBabloParser:
    """Test suite for BabloParser class."""

    @pytest.fixture
    def parser(self) -> BabloParser:
        """Create parser instance."""
        return BabloParser()

    # =========================================================================
    # Basic Parsing Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_empty_message(self, parser):
        """Parser should return None for empty messages."""
        assert parser.parse("") is None
        assert parser.parse(None) is None

    @pytest.mark.unit
    def test_parse_no_match(self, parser):
        """Parser should return None for non-matching messages."""
        messages = [
            "This is just a regular message",
            "Hello world!",
            "BTC is going up",
            "Price alert: high volatility",
        ]
        for msg in messages:
            assert parser.parse(msg) is None

    # =========================================================================
    # Long Signal Tests (Green Squares)
    # =========================================================================

    @pytest.mark.unit
    def test_parse_long_signal_full(self, parser):
        """Parse complete long signal with all fields."""
        message = """[SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/)
🟩🟩🟩🟩🟩
`| 1м ТФ |`
**Качество = 7 из 10:**
  ° Профитность _8_ из 10
  ° Просадка _6_ из 10
  ° Точность _7_ из 10

**Вероятность (60 минут):**
`0.3%`: 📉 `86%`, 📈 `72%`
`0.6%`: 📉 `75%`, 📈 `60%`

Максимальная просадка = __6%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "SYNUSDT.P"
        assert result.direction == "long"
        assert result.strength == 5
        assert result.timeframe == "1m"
        assert result.quality_total == 7
        assert result.quality_profit == 8
        assert result.quality_drawdown == 6
        assert result.quality_accuracy == 7
        assert result.time_horizon == "60 минут"
        assert result.max_drawdown == Decimal("6")
        assert "0.3" in result.probabilities
        # Note: Parser extracts 📉 as "long" and 📈 as "short" based on regex group order
        assert result.probabilities["0.3"]["long"] == 86  # 📉 value
        assert result.probabilities["0.3"]["short"] == 72  # 📈 value

    @pytest.mark.unit
    def test_parse_long_minimal_strength(self, parser):
        """Parse long signal with minimal strength (1 square)."""
        message = """[BTCUSDT.P](https://example.com)
🟩
`| 15м ТФ |`
**Качество = 5 из 10:**

**Вероятность (2 часа):**
`1.0%`: 📉 `70%`, 📈 `65%`

Максимальная просадка = __10%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.direction == "long"
        assert result.strength == 1

    @pytest.mark.unit
    def test_parse_long_max_strength(self, parser):
        """Parse long signal with maximum strength (5+ squares)."""
        message = """[ETHUSDT.P](https://example.com)
🟩🟩🟩🟩🟩🟩🟩
`| 1м ТФ |`
**Качество = 10 из 10:**

**Вероятность (30 минут):**
`0.5%`: 📉 `90%`, 📈 `85%`

Максимальная просадка = __3%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.direction == "long"
        assert result.strength == 7  # All squares counted

    # =========================================================================
    # Short Signal Tests (Red Squares)
    # =========================================================================

    @pytest.mark.unit
    def test_parse_short_signal_full(self, parser):
        """Parse complete short signal with all fields."""
        message = """[BTCUSDT.P](https://ru.tradingview.com/symbols/BTCUSDT.P/)
🟥🟥🟥
`| 15м ТФ |`
**Качество = 8 из 10:**
  ° Профитность _10_ из 10
  ° Просадка _4_ из 10
  ° Точность _10_ из 10

**Вероятность (12 часов):**
`0.9%`: 📉 `82%`, 📈 `73%`
`1.5%`: 📉 `75%`, 📈 `66%`
`2.7%`: 📉 `55%`, 📈 `45%`

Максимальная просадка = __17%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT.P"
        assert result.direction == "short"
        assert result.strength == 3
        assert result.timeframe == "15m"
        assert result.quality_total == 8
        assert result.quality_profit == 10
        assert result.quality_drawdown == 4
        assert result.quality_accuracy == 10
        assert result.time_horizon == "12 часов"
        assert result.max_drawdown == Decimal("17")
        assert len(result.probabilities) == 3

    @pytest.mark.unit
    def test_parse_short_minimal(self, parser):
        """Parse minimal short signal."""
        message = """[XRPUSDT.P](https://example.com)
🟥
`| 4ч ТФ |`
**Качество = 3 из 10:**

**Вероятность (1 день):**
`2.0%`: 📉 `60%`, 📈 `55%`

Максимальная просадка = __25%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.direction == "short"
        assert result.strength == 1
        assert result.timeframe == "4h"

    # =========================================================================
    # Timeframe Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_timeframe_1m(self, parser):
        """Parse 1 minute timeframe."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (30 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.timeframe == "1m"

    @pytest.mark.unit
    def test_parse_timeframe_15m(self, parser):
        """Parse 15 minute timeframe."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 15м ТФ |`
**Качество = 5 из 10:**
**Вероятность (2 часа):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.timeframe == "15m"

    @pytest.mark.unit
    def test_parse_timeframe_30m(self, parser):
        """Parse 30 minute timeframe."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 30м ТФ |`
**Качество = 5 из 10:**
**Вероятность (4 часа):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.timeframe == "30m"

    @pytest.mark.unit
    def test_parse_timeframe_1h(self, parser):
        """Parse 1 hour timeframe."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 1ч ТФ |`
**Качество = 5 из 10:**
**Вероятность (12 часов):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.timeframe == "1h"

    @pytest.mark.unit
    def test_parse_timeframe_4h(self, parser):
        """Parse 4 hour timeframe."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 4ч ТФ |`
**Качество = 5 из 10:**
**Вероятность (2 дня):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.timeframe == "4h"

    # =========================================================================
    # Quality Metrics Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_quality_total(self, parser):
        """Parse total quality score."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩🟩
`| 1м ТФ |`
**Качество = 9 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.quality_total == 9

    @pytest.mark.unit
    def test_parse_quality_breakdown(self, parser):
        """Parse quality breakdown metrics."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩🟩
`| 1м ТФ |`
**Качество = 7 из 10:**
  ° Профитность _9_ из 10
  ° Просадка _5_ из 10
  ° Точность _8_ из 10
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.quality_profit == 9
        assert result.quality_drawdown == 5
        assert result.quality_accuracy == 8

    @pytest.mark.unit
    def test_parse_quality_edge_values(self, parser):
        """Parse quality with edge values (1 and 10)."""
        message = """[BTCUSDT.P](https://example.com)
🟩
`| 1м ТФ |`
**Качество = 1 из 10:**
  ° Профитность _1_ из 10
  ° Просадка _10_ из 10
  ° Точность _1_ из 10
**Вероятность (60 минут):**
`1%`: 📉 `50%`, 📈 `50%`
Максимальная просадка = __50%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.quality_total == 1
        assert result.quality_profit == 1
        assert result.quality_drawdown == 10
        assert result.quality_accuracy == 1

    # =========================================================================
    # Probability Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_single_probability(self, parser):
        """Parse signal with single probability target."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`0.5%`: 📉 `75%`, 📈 `70%`
Максимальная просадка = __8%__"""

        result = parser.parse(message)

        assert result is not None
        assert len(result.probabilities) == 1
        assert "0.5" in result.probabilities
        # Parser assigns: 📉 → "long", 📈 → "short"
        assert result.probabilities["0.5"]["long"] == 75  # 📉 value
        assert result.probabilities["0.5"]["short"] == 70  # 📈 value

    @pytest.mark.unit
    def test_parse_multiple_probabilities(self, parser):
        """Parse signal with multiple probability targets."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩🟩
`| 1м ТФ |`
**Качество = 6 из 10:**
**Вероятность (60 минут):**
`0.3%`: 📉 `90%`, 📈 `85%`
`0.6%`: 📉 `80%`, 📈 `75%`
`0.9%`: 📉 `70%`, 📈 `65%`
`1.2%`: 📉 `60%`, 📈 `55%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert len(result.probabilities) == 4
        # Parser assigns: 📉 → "long", 📈 → "short"
        assert result.probabilities["0.3"]["long"] == 90  # 📉 value
        assert result.probabilities["0.3"]["short"] == 85  # 📈 value
        assert result.probabilities["1.2"]["long"] == 60  # 📉 value
        assert result.probabilities["1.2"]["short"] == 55  # 📈 value

    # =========================================================================
    # Time Horizon Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_time_horizon_minutes(self, parser):
        """Parse time horizon in minutes."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.time_horizon == "60 минут"

    @pytest.mark.unit
    def test_parse_time_horizon_hours(self, parser):
        """Parse time horizon in hours."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 15м ТФ |`
**Качество = 5 из 10:**
**Вероятность (12 часов):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.time_horizon == "12 часов"

    @pytest.mark.unit
    def test_parse_time_horizon_days(self, parser):
        """Parse time horizon in days."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 4ч ТФ |`
**Качество = 5 из 10:**
**Вероятность (2 дня):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.time_horizon == "2 дня"

    # =========================================================================
    # Max Drawdown Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_max_drawdown_small(self, parser):
        """Parse small max drawdown value."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩🟩🟩🟩
`| 1м ТФ |`
**Качество = 9 из 10:**
**Вероятность (30 минут):**
`0.3%`: 📉 `95%`, 📈 `90%`
Максимальная просадка = __2%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.max_drawdown == Decimal("2")

    @pytest.mark.unit
    def test_parse_max_drawdown_large(self, parser):
        """Parse large max drawdown value."""
        message = """[BTCUSDT.P](https://example.com)
🟥
`| 4ч ТФ |`
**Качество = 2 из 10:**
**Вероятность (3 дня):**
`5%`: 📉 `55%`, 📈 `50%`
Максимальная просадка = __45%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.max_drawdown == Decimal("45")

    # =========================================================================
    # Symbol Format Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_symbol_with_p_suffix(self, parser):
        """Parse symbol with .P suffix (perpetual)."""
        message = """[SYNUSDT.P](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "SYNUSDT.P"

    @pytest.mark.unit
    def test_parse_symbol_without_suffix(self, parser):
        """Parse symbol without .P suffix."""
        message = """[BTCUSDT](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT"

    @pytest.mark.unit
    def test_parse_various_symbols(self, parser):
        """Test parsing of various symbol formats."""
        symbols = ["ETHUSDT.P", "XRPUSDT.P", "DOGEUSDT.P", "1000PEPEUSDT.P", "SOLUSDT.P"]

        for symbol in symbols:
            message = f"""[{symbol}](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

            result = parser.parse(message)
            assert result is not None, f"Failed to parse symbol: {symbol}"
            assert result.symbol == symbol

    # =========================================================================
    # Edge Cases
    # =========================================================================

    @pytest.mark.unit
    def test_parse_missing_direction(self, parser):
        """Parser should return None when direction is missing."""
        message = """[BTCUSDT.P](https://example.com)
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is None

    @pytest.mark.unit
    def test_parse_missing_symbol(self, parser):
        """Parser should return None when symbol is missing."""
        message = """🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is None

    @pytest.mark.unit
    def test_parse_missing_timeframe(self, parser):
        """Parser should return None when timeframe is missing."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is None

    @pytest.mark.unit
    def test_parse_missing_quality(self, parser):
        """Parser should return None when quality is missing."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 1м ТФ |`
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is None

    @pytest.mark.unit
    def test_parse_raw_message_stored(self, parser):
        """Parsed signal should store raw message."""
        message = """[BTCUSDT.P](https://example.com)
🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**
**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __5%__"""

        result = parser.parse(message)

        assert result is not None
        assert result.raw_message == message

    @pytest.mark.unit
    def test_parse_whitespace_handling(self, parser):
        """Parser should handle extra whitespace."""
        message = """  [BTCUSDT.P](https://example.com)

🟩🟩🟩

`| 1м ТФ |`

**Качество = 5 из 10:**


**Вероятность (60 минут):**
`1%`: 📉 `70%`, 📈 `65%`

Максимальная просадка = __5%__  """

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT.P"


class TestParsedBabloSignalDataclass:
    """Tests for ParsedBabloSignal dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default values of ParsedBabloSignal."""
        signal = ParsedBabloSignal(
            symbol="BTCUSDT.P",
            direction="long",
            strength=3,
            timeframe="1m",
        )

        assert signal.symbol == "BTCUSDT.P"
        assert signal.direction == "long"
        assert signal.strength == 3
        assert signal.timeframe == "1m"
        assert signal.time_horizon is None
        assert signal.quality_total == 0
        assert signal.quality_profit is None
        assert signal.quality_drawdown is None
        assert signal.quality_accuracy is None
        assert signal.probabilities == {}
        assert signal.max_drawdown is None
        assert signal.raw_message is None

    @pytest.mark.unit
    def test_all_values(self):
        """Test ParsedBabloSignal with all values set."""
        signal = ParsedBabloSignal(
            symbol="SYNUSDT.P",
            direction="short",
            strength=5,
            timeframe="15m",
            time_horizon="12 часов",
            quality_total=8,
            quality_profit=9,
            quality_drawdown=7,
            quality_accuracy=8,
            probabilities={"0.5": {"long": 70, "short": 75}},
            max_drawdown=Decimal("10"),
            raw_message="test message",
        )

        assert signal.symbol == "SYNUSDT.P"
        assert signal.direction == "short"
        assert signal.strength == 5
        assert signal.timeframe == "15m"
        assert signal.time_horizon == "12 часов"
        assert signal.quality_total == 8
        assert signal.quality_profit == 9
        assert signal.quality_drawdown == 7
        assert signal.quality_accuracy == 8
        assert signal.probabilities == {"0.5": {"long": 70, "short": 75}}
        assert signal.max_drawdown == Decimal("10")
        assert signal.raw_message == "test message"


class TestBabloParserInternalMethods:
    """Tests for internal BabloParser methods."""

    @pytest.fixture
    def parser(self) -> BabloParser:
        """Create parser instance."""
        return BabloParser()

    @pytest.mark.unit
    def test_extract_direction_long(self, parser):
        """Test direction extraction for long signals."""
        message = "🟩🟩🟩🟩"
        direction, strength = parser._extract_direction_and_strength(message)

        assert direction == "long"
        assert strength == 4

    @pytest.mark.unit
    def test_extract_direction_short(self, parser):
        """Test direction extraction for short signals."""
        message = "🟥🟥"
        direction, strength = parser._extract_direction_and_strength(message)

        assert direction == "short"
        assert strength == 2

    @pytest.mark.unit
    def test_extract_direction_none(self, parser):
        """Test direction extraction when no squares present."""
        message = "No squares here"
        direction, strength = parser._extract_direction_and_strength(message)

        assert direction is None
        assert strength == 0

    @pytest.mark.unit
    def test_extract_pattern_int(self, parser):
        """Test integer pattern extraction."""
        message = "Профитность _8_ из 10"
        result = parser._extract_pattern_int(message, parser.PROFIT_PATTERN)

        assert result == 8

    @pytest.mark.unit
    def test_extract_pattern_int_no_match(self, parser):
        """Test integer pattern extraction with no match."""
        message = "No pattern here"
        result = parser._extract_pattern_int(message, parser.PROFIT_PATTERN)

        assert result is None

    @pytest.mark.unit
    def test_extract_probabilities(self, parser):
        """Test probability extraction."""
        message = """`0.3%`: 📉 `86%`, 📈 `72%`
`0.6%`: 📉 `75%`, 📈 `60%`"""

        result = parser._extract_probabilities(message)

        assert len(result) == 2
        # Parser assigns: 📉 → "long", 📈 → "short"
        assert result["0.3"]["long"] == 86  # 📉 value
        assert result["0.3"]["short"] == 72  # 📈 value
        assert result["0.6"]["long"] == 75  # 📉 value
        assert result["0.6"]["short"] == 60  # 📈 value

    @pytest.mark.unit
    def test_extract_max_drawdown(self, parser):
        """Test max drawdown extraction."""
        message = "Максимальная просадка = __15%__"
        result = parser._extract_max_drawdown(message)

        assert result == Decimal("15")

    @pytest.mark.unit
    def test_extract_time_horizon(self, parser):
        """Test time horizon extraction."""
        message = "**Вероятность (60 минут):**"
        result = parser._extract_time_horizon(message)

        assert result == "60 минут"

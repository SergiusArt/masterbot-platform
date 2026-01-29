"""Unit tests for ImpulseParser."""

from decimal import Decimal
from unittest.mock import MagicMock, patch
import sys
import os

import pytest

# Add project paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "impulse_service"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))

# Mock the logger before importing parser
sys.modules['shared.utils.logger'] = MagicMock()
sys.modules['shared.utils'] = MagicMock()

from core.parser import ImpulseParser, ParsedImpulse


class TestImpulseParser:
    """Test suite for ImpulseParser class."""

    @pytest.fixture
    def parser(self) -> ImpulseParser:
        """Create parser instance."""
        return ImpulseParser()

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
            "12345",
        ]
        for msg in messages:
            assert parser.parse(msg) is None

    # =========================================================================
    # Pattern 1: Markdown Link Format [SYMBOL](url) **percent%**
    # =========================================================================

    @pytest.mark.unit
    def test_parse_markdown_growth_signal(self, parser):
        """Parse growth signal with markdown link format."""
        message = """🟢[SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/) **10%**
📈|29%|---|71%|📉
Максимальный импульс: 15%"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "SYNUSDT.P"
        assert result.percent == Decimal("10")
        assert result.type == "growth"
        assert result.max_percent == Decimal("15")
        assert result.growth_ratio == Decimal("29")
        assert result.fall_ratio == Decimal("71")

    @pytest.mark.unit
    def test_parse_markdown_fall_signal(self, parser):
        """Parse fall signal with markdown link format."""
        message = """🔴[AXSUSDT.P](https://ru.tradingview.com/symbols/AXSUSDT.P/) **-15%**
📈|35%|---|65%|📉
Максимальный импульс: 25%"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "AXSUSDT.P"
        assert result.percent == Decimal("-15")
        assert result.type == "fall"
        assert result.max_percent == Decimal("25")
        assert result.growth_ratio == Decimal("35")
        assert result.fall_ratio == Decimal("65")

    @pytest.mark.unit
    def test_parse_markdown_decimal_percent(self, parser):
        """Parse signal with decimal percent value."""
        message = "[BTCUSDT.P](https://example.com) **12.5%**"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT.P"
        assert result.percent == Decimal("12.5")
        assert result.type == "growth"

    @pytest.mark.unit
    def test_parse_markdown_without_p_suffix(self, parser):
        """Parse signal without .P suffix."""
        message = "[ETHUSDT](https://example.com) **8%**"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "ETHUSDT"
        assert result.percent == Decimal("8")

    # =========================================================================
    # Pattern 2: Simple Format SYMBOL percent%
    # =========================================================================

    @pytest.mark.unit
    def test_parse_simple_growth(self, parser):
        """Parse simple growth signal."""
        message = "BTCUSDT +25.5%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT"
        assert result.percent == Decimal("25.5")
        assert result.type == "growth"

    @pytest.mark.unit
    def test_parse_simple_fall(self, parser):
        """Parse simple fall signal."""
        message = "ETHUSDT -12.3%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "ETHUSDT"
        assert result.percent == Decimal("-12.3")
        assert result.type == "fall"

    @pytest.mark.unit
    def test_parse_simple_busd_pair(self, parser):
        """Parse simple signal with BUSD pair."""
        message = "BNBBUSD +5%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BNBBUSD"
        assert result.percent == Decimal("5")

    @pytest.mark.unit
    def test_parse_simple_without_sign(self, parser):
        """Parse simple signal without explicit + sign."""
        message = "SOLUSDT 18%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "SOLUSDT"
        assert result.percent == Decimal("18")
        assert result.type == "growth"

    # =========================================================================
    # Pattern 3: Ratio Format BASE/QUOTE: percent%
    # =========================================================================

    @pytest.mark.unit
    def test_parse_ratio_format(self, parser):
        """Parse ratio format signal."""
        message = "BTC/USDT: 15.5%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT"
        assert result.percent == Decimal("15.5")

    @pytest.mark.unit
    def test_parse_ratio_format_negative(self, parser):
        """Parse ratio format fall signal."""
        message = "ETH/BTC: -8.2%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "ETHBTC"
        assert result.percent == Decimal("-8.2")
        assert result.type == "fall"

    # =========================================================================
    # Pattern 4: Dollar Format $SYMBOL percent%
    # =========================================================================

    @pytest.mark.unit
    def test_parse_dollar_format(self, parser):
        """Parse dollar format signal."""
        message = "$BTC +8.7%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTC"
        assert result.percent == Decimal("8.7")

    @pytest.mark.unit
    def test_parse_dollar_format_negative(self, parser):
        """Parse dollar format fall signal."""
        message = "$ETH -5.5%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "ETH"
        assert result.percent == Decimal("-5.5")
        assert result.type == "fall"

    # =========================================================================
    # Max Percent Extraction Tests
    # =========================================================================

    @pytest.mark.unit
    def test_extract_max_percent_russian(self, parser):
        """Extract max percent with Russian label."""
        message = """[BTCUSDT](https://example.com) **10%**
Максимальный импульс: 91%"""

        result = parser.parse(message)

        assert result is not None
        assert result.max_percent == Decimal("91")

    @pytest.mark.unit
    def test_extract_max_percent_english(self, parser):
        """Extract max percent with English label."""
        message = """[BTCUSDT](https://example.com) **10%**
max: 25.5%"""

        result = parser.parse(message)

        assert result is not None
        assert result.max_percent == Decimal("25.5")

    @pytest.mark.unit
    def test_no_max_percent(self, parser):
        """Return None when max percent is not present."""
        message = "[BTCUSDT](https://example.com) **10%**"

        result = parser.parse(message)

        assert result is not None
        assert result.max_percent is None

    # =========================================================================
    # Ratio Extraction Tests
    # =========================================================================

    @pytest.mark.unit
    def test_extract_ratios_emoji_format(self, parser):
        """Extract ratios from emoji format."""
        message = """[SYNUSDT.P](https://example.com) **10%**
📈|29%|---|71%|📉"""

        result = parser.parse(message)

        assert result is not None
        assert result.growth_ratio == Decimal("29")
        assert result.fall_ratio == Decimal("71")

    @pytest.mark.unit
    def test_extract_ratios_gf_format(self, parser):
        """Extract ratios from G/F format."""
        message = """[BTCUSDT](https://example.com) **15%**
G/F: 3.5/2.1"""

        result = parser.parse(message)

        assert result is not None
        assert result.growth_ratio == Decimal("3.5")
        assert result.fall_ratio == Decimal("2.1")

    @pytest.mark.unit
    def test_no_ratios(self, parser):
        """Return None when ratios are not present."""
        message = "[BTCUSDT](https://example.com) **10%**"

        result = parser.parse(message)

        assert result is not None
        assert result.growth_ratio is None
        assert result.fall_ratio is None

    # =========================================================================
    # Edge Cases and Boundary Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_zero_percent(self, parser):
        """Handle zero percent correctly."""
        message = "BTCUSDT 0%"

        result = parser.parse(message)

        assert result is not None
        assert result.percent == Decimal("0")
        assert result.type == "growth"  # 0 is considered growth

    @pytest.mark.unit
    def test_parse_very_large_percent(self, parser):
        """Handle very large percent values."""
        message = "BTCUSDT +999%"

        result = parser.parse(message)

        assert result is not None
        assert result.percent == Decimal("999")

    @pytest.mark.unit
    def test_parse_small_decimal_percent(self, parser):
        """Handle small decimal percent values."""
        message = "BTCUSDT 0.1%"

        result = parser.parse(message)

        assert result is not None
        assert result.percent == Decimal("0.1")

    @pytest.mark.unit
    def test_case_insensitivity(self, parser):
        """Parser should handle different cases."""
        # Symbols should be uppercased
        message = "btcusdt +10%"

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT"

    @pytest.mark.unit
    def test_whitespace_handling(self, parser):
        """Parser should handle extra whitespace."""
        message = "  BTCUSDT   +15%  "

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT"
        assert result.percent == Decimal("15")

    @pytest.mark.unit
    def test_multiline_message(self, parser):
        """Parser should work with multiline messages."""
        message = """
Some header text

🟢[BTCUSDT.P](https://example.com) **20%**
📈|40%|---|60%|📉
Максимальный импульс: 30%

Some footer text
"""

        result = parser.parse(message)

        assert result is not None
        assert result.symbol == "BTCUSDT.P"
        assert result.percent == Decimal("20")
        assert result.max_percent == Decimal("30")
        assert result.growth_ratio == Decimal("40")
        assert result.fall_ratio == Decimal("60")

    # =========================================================================
    # Type Detection Tests
    # =========================================================================

    @pytest.mark.unit
    def test_positive_is_growth(self, parser):
        """Positive percent should be classified as growth."""
        message = "BTCUSDT +15%"

        result = parser.parse(message)

        assert result is not None
        assert result.type == "growth"

    @pytest.mark.unit
    def test_negative_is_fall(self, parser):
        """Negative percent should be classified as fall."""
        message = "BTCUSDT -15%"

        result = parser.parse(message)

        assert result is not None
        assert result.type == "fall"

    @pytest.mark.unit
    def test_zero_is_growth(self, parser):
        """Zero percent should be classified as growth."""
        message = "BTCUSDT 0%"

        result = parser.parse(message)

        assert result is not None
        assert result.type == "growth"

    # =========================================================================
    # Symbol Format Tests
    # =========================================================================

    @pytest.mark.unit
    def test_various_symbol_formats(self, parser):
        """Test parsing of various symbol formats."""
        test_cases = [
            ("BTCUSDT +10%", "BTCUSDT"),
            ("ETHBUSD +10%", "ETHBUSD"),
            ("BNBUSDC +10%", "BNBUSDC"),
            ("XRPBTC +10%", "XRPBTC"),
            ("DOGEETH +10%", "DOGEETH"),
            ("[1000PEPEUSDT.P](https://example.com) **10%**", "1000PEPEUSDT.P"),
        ]

        for message, expected_symbol in test_cases:
            result = parser.parse(message)
            assert result is not None, f"Failed to parse: {message}"
            assert result.symbol == expected_symbol, f"Expected {expected_symbol}, got {result.symbol}"


class TestParsedImpulseDataclass:
    """Tests for ParsedImpulse dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default values of ParsedImpulse."""
        impulse = ParsedImpulse(
            symbol="BTCUSDT",
            percent=Decimal("10"),
        )

        assert impulse.symbol == "BTCUSDT"
        assert impulse.percent == Decimal("10")
        assert impulse.max_percent is None
        assert impulse.type == "growth"
        assert impulse.growth_ratio is None
        assert impulse.fall_ratio is None

    @pytest.mark.unit
    def test_all_values(self):
        """Test ParsedImpulse with all values set."""
        impulse = ParsedImpulse(
            symbol="SYNUSDT.P",
            percent=Decimal("15.5"),
            max_percent=Decimal("25"),
            type="growth",
            growth_ratio=Decimal("65"),
            fall_ratio=Decimal("35"),
        )

        assert impulse.symbol == "SYNUSDT.P"
        assert impulse.percent == Decimal("15.5")
        assert impulse.max_percent == Decimal("25")
        assert impulse.type == "growth"
        assert impulse.growth_ratio == Decimal("65")
        assert impulse.fall_ratio == Decimal("35")

"""Unit tests for StrongParser."""

from unittest.mock import MagicMock
import sys

import pytest

# Mock the logger before importing parser
sys.modules['shared.utils.logger'] = MagicMock()
sys.modules['shared.utils'] = MagicMock()

from core.parser import StrongParser, ParsedStrongSignal


class TestStrongParser:
    """Test suite for StrongParser class."""

    @pytest.fixture
    def parser(self) -> StrongParser:
        """Create parser instance."""
        return StrongParser()

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
    # Long Signal Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_long_signal_plain(self, parser):
        """Parser should recognize plain long signal."""
        result = parser.parse("🧤DOTUSDT.P Long🧤")
        assert result is not None
        assert result.symbol == "DOTUSDT"
        assert result.direction == "long"

    @pytest.mark.unit
    def test_parse_long_signal_markdown(self, parser):
        """Parser should recognize markdown long signal."""
        result = parser.parse("🧤*DOTUSDT.P* _Long_🧤")
        assert result is not None
        assert result.symbol == "DOTUSDT"
        assert result.direction == "long"

    @pytest.mark.unit
    def test_parse_long_signal_solusdt(self, parser):
        """Parser should parse SOLUSDT long signal."""
        result = parser.parse("🧤SOLUSDT.P Long🧤")
        assert result is not None
        assert result.symbol == "SOLUSDT"
        assert result.direction == "long"

    @pytest.mark.unit
    def test_parse_long_signal_no_suffix(self, parser):
        """Parser should handle symbol without .P suffix."""
        result = parser.parse("🧤BTCUSDT Long🧤")
        assert result is not None
        assert result.symbol == "BTCUSDT"
        assert result.direction == "long"

    # =========================================================================
    # Short Signal Tests
    # =========================================================================

    @pytest.mark.unit
    def test_parse_short_signal_plain(self, parser):
        """Parser should recognize plain short signal."""
        result = parser.parse("🎒SOLUSDT.P Short🎒")
        assert result is not None
        assert result.symbol == "SOLUSDT"
        assert result.direction == "short"

    @pytest.mark.unit
    def test_parse_short_signal_markdown(self, parser):
        """Parser should recognize markdown short signal."""
        result = parser.parse("🎒*SOLUSDT.P* _Short_🎒")
        assert result is not None
        assert result.symbol == "SOLUSDT"
        assert result.direction == "short"

    @pytest.mark.unit
    def test_parse_short_signal_ethusdt(self, parser):
        """Parser should parse ETHUSDT short signal."""
        result = parser.parse("🎒ETHUSDT.P Short🎒")
        assert result is not None
        assert result.symbol == "ETHUSDT"
        assert result.direction == "short"

    # =========================================================================
    # Raw Message Preservation
    # =========================================================================

    @pytest.mark.unit
    def test_raw_message_preserved(self, parser):
        """Parser should preserve raw message."""
        msg = "🧤DOTUSDT.P Long🧤"
        result = parser.parse(msg)
        assert result is not None
        assert result.raw_message == msg

    # =========================================================================
    # Symbol Cleaning
    # =========================================================================

    @pytest.mark.unit
    def test_symbol_p_suffix_stripped(self, parser):
        """Parser should strip .P suffix from symbols."""
        result = parser.parse("🧤XRPUSDT.P Long🧤")
        assert result is not None
        assert result.symbol == "XRPUSDT"

    @pytest.mark.unit
    def test_symbol_without_p_suffix_unchanged(self, parser):
        """Parser should not modify symbols without .P suffix."""
        result = parser.parse("🧤BTCUSDT Long🧤")
        assert result is not None
        assert result.symbol == "BTCUSDT"

    # =========================================================================
    # Edge Cases
    # =========================================================================

    @pytest.mark.unit
    def test_mixed_emojis_no_match(self, parser):
        """Parser should not match mixed emojis."""
        assert parser.parse("🧤DOTUSDT.P Short🎒") is None
        assert parser.parse("🎒DOTUSDT.P Long🧤") is None

    @pytest.mark.unit
    def test_case_insensitive_direction(self, parser):
        """Parser should handle case-insensitive directions."""
        result = parser.parse("🧤DOTUSDT.P long🧤")
        assert result is not None
        assert result.direction == "long"

        result = parser.parse("🎒DOTUSDT.P short🎒")
        assert result is not None
        assert result.direction == "short"

    @pytest.mark.unit
    def test_parse_with_1000_symbol(self, parser):
        """Parser should handle 1000-prefixed symbols."""
        result = parser.parse("🧤1000PEPEUSDT.P Long🧤")
        assert result is not None
        assert result.symbol == "1000PEPEUSDT"
        assert result.direction == "long"

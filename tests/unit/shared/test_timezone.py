"""Tests for timezone utilities."""

import pytest
from datetime import datetime, timezone, timedelta

import sys
import os

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))


class TestParseUtcOffset:
    """Tests for parse_utc_offset function."""

    @pytest.mark.unit
    def test_positive_offset_with_plus(self):
        """Test parsing positive offset with + sign."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset("+3") == 3
        assert parse_utc_offset("+5") == 5
        assert parse_utc_offset("+12") == 12

    @pytest.mark.unit
    def test_positive_offset_without_sign(self):
        """Test parsing positive offset without sign."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset("3") == 3
        assert parse_utc_offset("5") == 5
        assert parse_utc_offset("0") == 0

    @pytest.mark.unit
    def test_negative_offset(self):
        """Test parsing negative offset."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset("-5") == -5
        assert parse_utc_offset("-12") == -12
        assert parse_utc_offset("-1") == -1

    @pytest.mark.unit
    def test_padded_offset(self):
        """Test parsing offset with leading zero."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset("+03") == 3
        assert parse_utc_offset("-05") == -5
        assert parse_utc_offset("00") == 0

    @pytest.mark.unit
    def test_offset_with_minutes(self):
        """Test parsing offset with minutes (ignores minutes)."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset("+3:00") == 3
        assert parse_utc_offset("-5:30") == -5

    @pytest.mark.unit
    def test_invalid_offset(self):
        """Test parsing invalid offset returns None."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset("abc") is None
        assert parse_utc_offset("") is None
        assert parse_utc_offset("+15") is None  # Out of range (>14)
        assert parse_utc_offset("++3") is None
        assert parse_utc_offset("3.5") is None

    @pytest.mark.unit
    def test_whitespace_handling(self):
        """Test offset with whitespace is trimmed."""
        from shared.utils.timezone import parse_utc_offset

        assert parse_utc_offset(" +3 ") == 3
        assert parse_utc_offset("  -5  ") == -5


class TestValidateTimezoneInput:
    """Tests for validate_timezone_input function."""

    @pytest.mark.unit
    def test_valid_positive_offset(self):
        """Test valid positive offset normalization."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("+3")
        assert is_valid is True
        assert normalized == "UTC+3"
        assert error is None

    @pytest.mark.unit
    def test_valid_negative_offset(self):
        """Test valid negative offset normalization."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("-5")
        assert is_valid is True
        assert normalized == "UTC-5"
        assert error is None

    @pytest.mark.unit
    def test_valid_zero_offset(self):
        """Test zero offset normalization."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("0")
        assert is_valid is True
        assert normalized == "UTC+0"
        assert error is None

    @pytest.mark.unit
    def test_utc_prefix_removed(self):
        """Test UTC prefix is handled."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("UTC+3")
        assert is_valid is True
        assert normalized == "UTC+3"

        is_valid, normalized, error = validate_timezone_input("utc-5")
        assert is_valid is True
        assert normalized == "UTC-5"

    @pytest.mark.unit
    def test_invalid_format(self):
        """Test invalid format returns error."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("abc")
        assert is_valid is False
        assert normalized is None
        assert error is not None
        assert "Неверный формат" in error

    @pytest.mark.unit
    def test_out_of_range(self):
        """Test out of range offset returns error."""
        from shared.utils.timezone import validate_timezone_input

        # -13 is out of range (min is -12)
        is_valid, normalized, error = validate_timezone_input("-13")
        assert is_valid is False
        assert normalized is None
        assert error is not None

    @pytest.mark.unit
    def test_max_offset(self):
        """Test maximum valid offset (+14)."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("+14")
        assert is_valid is True
        assert normalized == "UTC+14"

    @pytest.mark.unit
    def test_min_offset(self):
        """Test minimum valid offset (-12)."""
        from shared.utils.timezone import validate_timezone_input

        is_valid, normalized, error = validate_timezone_input("-12")
        assert is_valid is True
        assert normalized == "UTC-12"


class TestGetPytzTimezone:
    """Tests for get_pytz_timezone function."""

    @pytest.mark.unit
    def test_utc_offset_positive(self):
        """Test UTC offset positive timezone."""
        from shared.utils.timezone import get_pytz_timezone

        tz = get_pytz_timezone("UTC+3")
        assert tz == timezone(timedelta(hours=3))

    @pytest.mark.unit
    def test_utc_offset_negative(self):
        """Test UTC offset negative timezone."""
        from shared.utils.timezone import get_pytz_timezone

        tz = get_pytz_timezone("UTC-5")
        assert tz == timezone(timedelta(hours=-5))

    @pytest.mark.unit
    def test_utc_zero(self):
        """Test UTC+0 timezone."""
        from shared.utils.timezone import get_pytz_timezone

        tz = get_pytz_timezone("UTC+0")
        assert tz == timezone(timedelta(hours=0))

    @pytest.mark.unit
    def test_plain_utc(self):
        """Test plain UTC string."""
        from shared.utils.timezone import get_pytz_timezone

        tz = get_pytz_timezone("UTC")
        assert tz == timezone.utc

    @pytest.mark.unit
    def test_named_timezone(self):
        """Test named timezone (pytz)."""
        from shared.utils.timezone import get_pytz_timezone
        import pytz

        tz = get_pytz_timezone("Europe/Moscow")
        assert isinstance(tz, pytz.BaseTzInfo)
        assert tz.zone == "Europe/Moscow"

    @pytest.mark.unit
    def test_invalid_timezone_fallback(self):
        """Test invalid timezone falls back to UTC."""
        from shared.utils.timezone import get_pytz_timezone

        tz = get_pytz_timezone("Invalid/Timezone")
        assert tz == timezone.utc


class TestConvertToUserTimezone:
    """Tests for convert_to_user_timezone function."""

    @pytest.mark.unit
    def test_convert_utc_to_moscow(self):
        """Test converting UTC to Moscow time."""
        from shared.utils.timezone import convert_to_user_timezone

        dt_utc = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        dt_moscow = convert_to_user_timezone(dt_utc, "Europe/Moscow")

        # Moscow is UTC+3
        assert dt_moscow.hour == 13
        assert dt_moscow.day == 15

    @pytest.mark.unit
    def test_convert_utc_to_utc_offset(self):
        """Test converting UTC to UTC offset timezone."""
        from shared.utils.timezone import convert_to_user_timezone

        dt_utc = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        dt_plus5 = convert_to_user_timezone(dt_utc, "UTC+5")

        assert dt_plus5.hour == 15
        assert dt_plus5.day == 15

    @pytest.mark.unit
    def test_convert_naive_datetime(self):
        """Test converting naive datetime (assumes UTC)."""
        from shared.utils.timezone import convert_to_user_timezone

        dt_naive = datetime(2024, 1, 15, 10, 0, 0)
        dt_plus3 = convert_to_user_timezone(dt_naive, "UTC+3")

        assert dt_plus3.hour == 13

    @pytest.mark.unit
    def test_convert_negative_offset(self):
        """Test converting to negative offset timezone."""
        from shared.utils.timezone import convert_to_user_timezone

        dt_utc = datetime(2024, 1, 15, 5, 0, 0, tzinfo=timezone.utc)
        dt_minus5 = convert_to_user_timezone(dt_utc, "UTC-5")

        # 5:00 UTC - 5 hours = 0:00 same day
        assert dt_minus5.hour == 0
        assert dt_minus5.day == 15


class TestGetUtcOffsetDisplay:
    """Tests for get_utc_offset_display function."""

    @pytest.mark.unit
    def test_utc_offset_passthrough(self):
        """Test UTC offset string passes through."""
        from shared.utils.timezone import get_utc_offset_display

        assert get_utc_offset_display("UTC+3") == "UTC+3"
        assert get_utc_offset_display("UTC-5") == "UTC-5"
        assert get_utc_offset_display("UTC+0") == "UTC+0"

    @pytest.mark.unit
    def test_named_timezone_moscow(self):
        """Test named timezone returns offset."""
        from shared.utils.timezone import get_utc_offset_display

        result = get_utc_offset_display("Europe/Moscow")
        assert result == "UTC+3"

    @pytest.mark.unit
    def test_named_timezone_utc(self):
        """Test UTC timezone."""
        from shared.utils.timezone import get_utc_offset_display

        result = get_utc_offset_display("UTC")
        assert result in ["UTC+0", "UTC"]

    @pytest.mark.unit
    def test_invalid_timezone(self):
        """Test invalid timezone returns UTC+0."""
        from shared.utils.timezone import get_utc_offset_display

        result = get_utc_offset_display("Invalid/Zone")
        assert result == "UTC+0"

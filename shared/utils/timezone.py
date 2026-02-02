"""Timezone utilities for user timezone handling."""

import re
from datetime import datetime, timezone, timedelta
from typing import Optional

import pytz


def parse_utc_offset(offset_str: str) -> Optional[int]:
    """Parse UTC offset string to hours.

    Accepts formats:
    - "+3", "-5", "3", "5"
    - "+03", "-05"
    - "+3:00", "-5:30" (only full hours supported)

    Args:
        offset_str: UTC offset string

    Returns:
        Offset in hours or None if invalid
    """
    offset_str = offset_str.strip()

    # Match patterns like +3, -5, 3, +03, -05, +3:00
    match = re.match(r'^([+-])?(\d{1,2})(?::(\d{2}))?$', offset_str)
    if not match:
        return None

    sign = match.group(1) or '+'
    hours = int(match.group(2))
    # minutes = int(match.group(3) or 0)  # Ignore minutes for simplicity

    # Validate range (-12 to +14)
    if hours > 14:
        return None

    return hours if sign == '+' else -hours


def validate_timezone_input(user_input: str) -> tuple[bool, str | None, str | None]:
    """Validate and normalize user timezone input.

    Args:
        user_input: Raw user input (e.g., "+3", "-5", "3", "UTC+3")

    Returns:
        Tuple of (is_valid, normalized_value, error_message)
    """
    user_input = user_input.strip().upper()

    # Remove "UTC" prefix if present
    if user_input.startswith("UTC"):
        user_input = user_input[3:]

    # Parse the offset
    offset = parse_utc_offset(user_input)
    if offset is None:
        return False, None, (
            "Неверный формат. Введите число от -12 до +14.\n"
            "Примеры: +3, -5, 0, +5"
        )

    # Validate range
    if offset < -12 or offset > 14:
        return False, None, (
            "Часовой пояс должен быть от -12 до +14.\n"
            "Примеры: +3 (Москва), -5 (Нью-Йорк), 0 (Лондон)"
        )

    # Normalize to UTC+N format
    if offset >= 0:
        normalized = f"UTC+{offset}"
    else:
        normalized = f"UTC{offset}"

    return True, normalized, None


def get_pytz_timezone(tz_string: str) -> timezone | pytz.BaseTzInfo:
    """Get pytz/datetime timezone object from string.

    Args:
        tz_string: Timezone string ("Europe/Moscow" or "UTC+3")

    Returns:
        Timezone object
    """
    # Handle UTC offset format
    if tz_string.startswith("UTC"):
        offset_str = tz_string[3:]
        if offset_str:
            offset = parse_utc_offset(offset_str)
            if offset is not None:
                return timezone(timedelta(hours=offset))
        return timezone.utc

    # Try as pytz timezone name
    try:
        return pytz.timezone(tz_string)
    except pytz.UnknownTimeZoneError:
        # Fallback to UTC
        return timezone.utc


def convert_to_user_timezone(dt: datetime, user_tz: str) -> datetime:
    """Convert datetime to user's timezone.

    Args:
        dt: Datetime object (should be timezone-aware or assumed UTC)
        user_tz: User timezone string

    Returns:
        Datetime in user's timezone
    """
    # Ensure datetime is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    tz = get_pytz_timezone(user_tz)

    # Convert
    if isinstance(tz, pytz.BaseTzInfo):
        return dt.astimezone(tz)
    else:
        return dt.astimezone(tz)


def get_utc_offset_display(tz_string: str) -> str:
    """Get UTC offset display string for a timezone.

    Args:
        tz_string: Timezone string

    Returns:
        UTC offset like "UTC+3" or "UTC-5"
    """
    if tz_string.startswith("UTC"):
        return tz_string

    try:
        tz = pytz.timezone(tz_string)
        now = datetime.now(tz)
        offset = now.utcoffset()
        if offset:
            hours = int(offset.total_seconds() / 3600)
            if hours >= 0:
                return f"UTC+{hours}"
            else:
                return f"UTC{hours}"
    except Exception:
        pass

    return "UTC+0"

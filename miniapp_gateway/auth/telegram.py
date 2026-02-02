"""Telegram Mini App initData validation.

Based on Telegram Web Apps documentation:
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import parse_qs, unquote

from pydantic import BaseModel


class TelegramUser(BaseModel):
    """Telegram user data from initData."""

    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    allows_write_to_pm: Optional[bool] = None


class InitDataValidationResult(BaseModel):
    """Result of initData validation."""

    valid: bool
    user: Optional[TelegramUser] = None
    auth_date: Optional[datetime] = None
    error: Optional[str] = None


def validate_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int = 86400,
) -> InitDataValidationResult:
    """Validate Telegram Mini App initData.

    Args:
        init_data: Raw initData string from Telegram Mini App
        bot_token: Bot token for HMAC validation
        max_age_seconds: Maximum age of initData in seconds (default 24 hours)

    Returns:
        InitDataValidationResult with validation status and user data
    """
    if not init_data:
        return InitDataValidationResult(valid=False, error="Empty initData")

    try:
        # Parse query string
        parsed = parse_qs(init_data, keep_blank_values=True)

        # Extract hash
        received_hash = parsed.pop("hash", [None])[0]
        if not received_hash:
            return InitDataValidationResult(valid=False, error="Missing hash")

        # Build data-check-string (sorted alphabetically)
        data_check_arr = []
        for key in sorted(parsed.keys()):
            value = parsed[key][0]
            data_check_arr.append(f"{key}={value}")
        data_check_string = "\n".join(data_check_arr)

        # Create secret key: HMAC-SHA256(bot_token, "WebAppData")
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256,
        ).digest()

        # Calculate expected hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Compare hashes (constant-time comparison)
        if not hmac.compare_digest(calculated_hash, received_hash):
            return InitDataValidationResult(valid=False, error="Invalid hash")

        # Check auth_date for freshness
        auth_date_str = parsed.get("auth_date", [None])[0]
        if not auth_date_str:
            return InitDataValidationResult(valid=False, error="Missing auth_date")

        auth_date = datetime.fromtimestamp(int(auth_date_str), tz=timezone.utc)
        now = datetime.now(timezone.utc)
        age = (now - auth_date).total_seconds()

        if age > max_age_seconds:
            return InitDataValidationResult(
                valid=False,
                error=f"initData expired ({age:.0f}s old, max {max_age_seconds}s)",
            )

        # Parse user data
        user_json = parsed.get("user", [None])[0]
        if not user_json:
            return InitDataValidationResult(valid=False, error="Missing user data")

        user_data = json.loads(unquote(user_json))
        user = TelegramUser(**user_data)

        return InitDataValidationResult(
            valid=True,
            user=user,
            auth_date=auth_date,
        )

    except json.JSONDecodeError as e:
        return InitDataValidationResult(valid=False, error=f"Invalid JSON in user: {e}")
    except ValueError as e:
        return InitDataValidationResult(valid=False, error=f"Validation error: {e}")
    except Exception as e:
        return InitDataValidationResult(valid=False, error=f"Unexpected error: {e}")


def get_user_from_init_data(init_data: str, bot_token: str) -> Optional[TelegramUser]:
    """Convenience function to get user from initData.

    Returns None if validation fails.
    """
    result = validate_init_data(init_data, bot_token)
    return result.user if result.valid else None

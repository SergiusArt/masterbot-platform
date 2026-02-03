"""FastAPI dependencies for Telegram authentication."""

from typing import Optional

from fastapi import Header, HTTPException, status

from auth.telegram import TelegramUser, validate_init_data
from config import settings


async def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
) -> TelegramUser:
    """Dependency to extract and validate Telegram user from initData.

    Args:
        x_telegram_init_data: Raw initData string from X-Telegram-Init-Data header

    Returns:
        Validated TelegramUser

    Raises:
        HTTPException 401 if validation fails
    """
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Telegram-Init-Data header",
        )

    result = validate_init_data(x_telegram_init_data, settings.BOT_TOKEN)

    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid initData: {result.error}",
        )

    return result.user


async def get_optional_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
) -> Optional[TelegramUser]:
    """Optional authentication - returns None if not authenticated.

    Useful for endpoints that work both authenticated and unauthenticated.
    """
    if not x_telegram_init_data:
        return None

    result = validate_init_data(x_telegram_init_data, settings.BOT_TOKEN)
    return result.user if result.valid else None

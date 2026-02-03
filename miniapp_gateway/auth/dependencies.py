"""FastAPI dependencies for Telegram authentication and access control."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.telegram import TelegramUser, validate_init_data
from config import settings
from database import get_db


async def check_user_access(user_id: int, db: AsyncSession) -> bool:
    """Check if user has access to Mini App.

    Access is granted if:
    1. User is admin (ADMIN_ID or is_admin=True in users table)
    2. User exists in users table, is_active=True, and access not expired

    Returns:
        True if user has access, False otherwise
    """
    import logging
    logger = logging.getLogger(__name__)

    # Admin always has access
    logger.info(f"Checking access for user_id={user_id} (type={type(user_id)}), ADMIN_ID={settings.ADMIN_ID} (type={type(settings.ADMIN_ID)})")
    if user_id == settings.ADMIN_ID:
        logger.info(f"User {user_id} is admin, granting access")
        return True

    # Check users table
    from sqlalchemy import text

    result = await db.execute(
        text("""
            SELECT is_active, is_admin, access_expires_at
            FROM users
            WHERE id = :user_id
        """),
        {"user_id": user_id},
    )
    row = result.fetchone()

    if not row:
        return False

    is_active, is_admin, access_expires_at = row

    # Admins always have access
    if is_admin:
        return True

    if not is_active:
        return False

    # Check if access hasn't expired (NULL = unlimited)
    if access_expires_at is None:
        return True

    return datetime.now(timezone.utc) < access_expires_at


async def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db),
) -> TelegramUser:
    """Dependency to extract, validate Telegram user, and check access.

    Args:
        x_telegram_init_data: Raw initData string from X-Telegram-Init-Data header
        db: Database session

    Returns:
        Validated TelegramUser with access

    Raises:
        HTTPException 401 if validation fails
        HTTPException 403 if user doesn't have access
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

    user = result.user

    # Check access
    has_access = await check_user_access(user.id, db)

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Contact @SrgArtManager for access.",
        )

    return user


async def get_optional_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
) -> Optional[TelegramUser]:
    """Optional authentication - returns None if not authenticated.

    Note: Does NOT check access control, only validates initData.
    """
    if not x_telegram_init_data:
        return None

    result = validate_init_data(x_telegram_init_data, settings.BOT_TOKEN)
    return result.user if result.valid else None

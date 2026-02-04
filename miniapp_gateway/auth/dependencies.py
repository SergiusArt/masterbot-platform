"""FastAPI dependencies for Telegram authentication and access control."""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from auth.telegram import TelegramUser, validate_init_data
from config import settings
from database import get_db, async_session_maker

logger = logging.getLogger(__name__)


async def check_user_access(user_id: int, db: AsyncSession) -> bool:
    """Check if user has access to Mini App.

    Access is granted if:
    1. User is admin (ADMIN_ID or is_admin=True in users table)
    2. User exists in users table, is_active=True, and access not expired

    Returns:
        True if user has access, False otherwise
    """
    # Admin always has access
    logger.debug(f"Checking access for user_id={user_id}, ADMIN_ID={settings.ADMIN_ID}")
    if user_id == settings.ADMIN_ID:
        logger.debug(f"User {user_id} is admin, granting access")
        return True

    # Check users table
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

    # Log user login activity (fire and forget, don't block the request)
    import asyncio
    asyncio.create_task(log_user_activity(user.id, "miniapp_login"))

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


async def log_user_activity(user_id: int, action: str, details: Optional[dict] = None) -> None:
    """Log user activity to action_logs table.

    Args:
        user_id: Telegram user ID
        action: Action name (e.g., 'miniapp_login', 'miniapp_view_impulses')
        details: Optional additional details as JSON
    """
    try:
        async with async_session_maker() as session:
            await session.execute(
                text("""
                    INSERT INTO action_logs (user_id, service_name, action, details, created_at)
                    VALUES (:user_id, 'miniapp', :action, :details::jsonb, NOW())
                """),
                {
                    "user_id": user_id,
                    "action": action,
                    "details": json.dumps(details or {}),
                }
            )
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to log user activity: {e}")


async def check_is_admin(user_id: int, db: AsyncSession) -> bool:
    """Check if user is admin.

    Args:
        user_id: Telegram user ID
        db: Database session

    Returns:
        True if user is admin, False otherwise
    """
    # Check ADMIN_ID first
    if user_id == settings.ADMIN_ID:
        return True

    # Check users table
    result = await db.execute(
        text("SELECT is_admin FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    row = result.fetchone()
    return row is not None and row[0] is True


async def get_admin_user(
    user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TelegramUser:
    """Dependency to ensure user is admin.

    Raises:
        HTTPException 403 if user is not admin
    """
    is_admin = await check_is_admin(user.id, db)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

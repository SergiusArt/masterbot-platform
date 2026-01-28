"""Authentication middleware."""

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy import select

from config import settings
from shared.database.connection import async_session_maker
from shared.database.models import User


class AuthMiddleware(BaseMiddleware):
    """Middleware for user authentication and access control."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        """Process incoming update."""
        user = event.from_user
        if not user:
            return

        user_id = user.id

        # Admin always has access
        if user_id == settings.ADMIN_ID:
            data["is_admin"] = True
            data["has_access"] = True
            data["db_user"] = None
            return await handler(event, data)

        # Check user in database
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            db_user = result.scalar_one_or_none()

            if db_user is None:
                # User not found - no access
                if isinstance(event, Message):
                    await event.answer(
                        "⛔ <b>Доступ запрещён</b>\n\n"
                        "У вас нет доступа к этому боту.\n"
                        "Обратитесь к администратору."
                    )
                return

            # Check if user is active
            if not db_user.is_active:
                if isinstance(event, Message):
                    await event.answer(
                        "⛔ <b>Доступ заблокирован</b>\n\n"
                        "Ваш аккаунт был деактивирован.\n"
                        "Обратитесь к администратору."
                    )
                return

            # Check access expiration
            if db_user.access_expires_at:
                if db_user.access_expires_at < datetime.now(timezone.utc):
                    if isinstance(event, Message):
                        await event.answer(
                            "⛔ <b>Доступ истёк</b>\n\n"
                            "Срок вашего доступа истёк.\n"
                            "Обратитесь к администратору для продления."
                        )
                    return

            # Update user info if changed
            if (
                db_user.username != user.username
                or db_user.first_name != user.first_name
                or db_user.last_name != user.last_name
            ):
                db_user.username = user.username
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
                await session.commit()

            data["is_admin"] = db_user.is_admin
            data["has_access"] = True
            data["db_user"] = db_user

        return await handler(event, data)

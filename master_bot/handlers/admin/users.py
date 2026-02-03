"""Admin users management handlers."""

from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from keyboards.reply.admin_menu import (
    get_admin_menu_keyboard,
    get_admin_users_keyboard,
)
from keyboards.reply.back import get_back_keyboard
from shared.database.connection import async_session_maker
from shared.database.models import User
from shared.constants import (
    MENU_USERS,
    MENU_ADD_USER,
    MENU_REMOVE_USER,
    MENU_EXTEND_ACCESS,
    MENU_USER_LIST,
    MENU_BACK,
)

router = Router()


class AdminUserState(StatesGroup):
    """States for user management."""

    waiting_for_user_id = State()
    waiting_for_days = State()
    action = State()


@router.message(F.text == MENU_USERS)
async def users_menu(message: Message, is_admin: bool = False) -> None:
    """Handle users menu button.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await message.answer(
        "👥 <b>Управление пользователями</b>\n\nВыберите действие:",
        reply_markup=get_admin_users_keyboard(),
    )


@router.message(F.text == MENU_ADD_USER)
async def add_user_start(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Start adding user flow.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await state.update_data(action="add")
    await state.set_state(AdminUserState.waiting_for_user_id)
    await message.answer(
        "➕ <b>Добавление пользователя</b>\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == MENU_REMOVE_USER)
async def remove_user_start(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Start removing user flow.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await state.update_data(action="remove")
    await state.set_state(AdminUserState.waiting_for_user_id)
    await message.answer(
        "➖ <b>Удаление пользователя</b>\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == MENU_EXTEND_ACCESS)
async def extend_access_start(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Start extending access flow.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await state.update_data(action="extend")
    await state.set_state(AdminUserState.waiting_for_user_id)
    await message.answer(
        "📅 <b>Продление доступа</b>\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == MENU_USER_LIST)
async def list_users(message: Message, is_admin: bool = False) -> None:
    """List all users.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    async with async_session_maker() as session:
        result = await session.execute(
            select(User).order_by(User.created_at.desc()).limit(50)
        )
        users = result.scalars().all()

    if not users:
        await message.answer("📋 Список пользователей пуст.")
        return

    lines = ["📋 <b>Список пользователей</b>\n"]

    for user in users:
        status = "✅" if user.is_active else "❌"
        admin = " 👑" if user.is_admin else ""

        # Build name display
        name_parts = []
        if user.first_name:
            name_parts.append(user.first_name)
        if user.username:
            name_parts.append(f"@{user.username}")
        name = " ".join(name_parts) if name_parts else "—"

        # Build expiration display
        if user.access_expires_at:
            expires = f"до {user.access_expires_at.strftime('%d.%m.%Y')}"
        else:
            expires = "♾ бессрочно"

        lines.append(f"{status}{admin} <code>{user.id}</code> | {name} | {expires}")

    await message.answer("\n".join(lines))


@router.message(AdminUserState.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext) -> None:
    """Process user ID input.

    Args:
        message: Incoming message
        state: FSM context
    """
    if message.text == MENU_BACK:
        await state.clear()
        await message.answer(
            "👥 <b>Управление пользователями</b>",
            reply_markup=get_admin_users_keyboard(),
        )
        return

    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Введите корректный Telegram ID (число).")
        return

    data = await state.get_data()
    action = data.get("action")

    if action == "add":
        async with async_session_maker() as session:
            existing = await session.get(User, user_id)
            if existing:
                await message.answer(f"⚠️ Пользователь {user_id} уже существует.")
                return

        await state.update_data(user_id=user_id)
        await state.set_state(AdminUserState.waiting_for_days)
        await message.answer(
            "Введите количество дней доступа (0 = бессрочно):",
        )

    elif action == "remove":
        async with async_session_maker() as session:
            user = await session.get(User, user_id)
            if not user:
                await message.answer(f"❌ Пользователь {user_id} не найден.")
                return

            user.is_active = False
            await session.commit()

        await state.clear()
        await message.answer(
            f"✅ Пользователь {user_id} деактивирован.",
            reply_markup=get_admin_users_keyboard(),
        )

    elif action == "extend":
        async with async_session_maker() as session:
            user = await session.get(User, user_id)
            if not user:
                await message.answer(f"❌ Пользователь {user_id} не найден.")
                return

        await state.update_data(user_id=user_id)
        await state.set_state(AdminUserState.waiting_for_days)
        await message.answer(
            "Введите количество дней для продления (0 = бессрочно):",
        )


@router.message(AdminUserState.waiting_for_days)
async def process_days(message: Message, state: FSMContext) -> None:
    """Process days input.

    Args:
        message: Incoming message
        state: FSM context
    """
    if message.text == MENU_BACK:
        await state.clear()
        await message.answer(
            "👥 <b>Управление пользователями</b>",
            reply_markup=get_admin_users_keyboard(),
        )
        return

    try:
        days = int(message.text.strip())
        if days < 0:
            raise ValueError("Negative days")
    except ValueError:
        await message.answer("❌ Введите корректное количество дней.")
        return

    data = await state.get_data()
    action = data.get("action")
    user_id = data.get("user_id")

    expires_at = None
    if days > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    async with async_session_maker() as session:
        if action == "add":
            user = User(
                id=user_id,
                is_active=True,
                access_expires_at=expires_at,
            )
            session.add(user)
            await session.commit()

            await message.answer(
                f"✅ Пользователь {user_id} добавлен.\n"
                f"Доступ: {'бессрочно' if days == 0 else f'{days} дней'}",
            )

        elif action == "extend":
            user = await session.get(User, user_id)
            if user:
                if days == 0:
                    # Unlimited access
                    user.access_expires_at = None
                    user.is_active = True
                    await session.commit()
                    await message.answer(
                        f"✅ Пользователю {user_id} установлен бессрочный доступ.",
                    )
                else:
                    if user.access_expires_at and user.access_expires_at > datetime.now(timezone.utc):
                        user.access_expires_at = user.access_expires_at + timedelta(days=days)
                    else:
                        user.access_expires_at = datetime.now(timezone.utc) + timedelta(days=days)
                    user.is_active = True
                    await session.commit()
                    await message.answer(
                        f"✅ Доступ пользователя {user_id} продлён на {days} дней.\n"
                        f"Новая дата: {user.access_expires_at.strftime('%d.%m.%Y')}",
                    )

    await state.clear()
    await message.answer(
        "👥 <b>Управление пользователями</b>",
        reply_markup=get_admin_users_keyboard(),
    )

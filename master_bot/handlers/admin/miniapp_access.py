"""Mini App access management handlers."""

from datetime import datetime, timedelta, timezone

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, text

from keyboards.reply.admin_menu import (
    get_admin_menu_keyboard,
    get_miniapp_access_keyboard,
    get_access_type_keyboard,
)
from keyboards.reply.back import get_back_keyboard
from shared.database.connection import async_session_maker
from shared.database.models import MiniAppAccess
from shared.constants import (
    MENU_MINIAPP,
    MENU_MINIAPP_ADD,
    MENU_MINIAPP_REMOVE,
    MENU_MINIAPP_EXTEND,
    MENU_MINIAPP_LIST,
    MENU_MINIAPP_UNLIMITED,
    MENU_MINIAPP_SUBSCRIPTION,
    MENU_BACK,
)

router = Router()


class MiniAppAccessState(StatesGroup):
    """States for Mini App access management."""

    waiting_for_user_id = State()
    waiting_for_access_type = State()
    waiting_for_days = State()
    action = State()


@router.message(F.text == MENU_MINIAPP)
async def miniapp_menu(message: Message, is_admin: bool = False) -> None:
    """Handle Mini App menu button.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await message.answer(
        "📱 <b>Управление Mini App</b>\n\n"
        "Управление доступом пользователей к Mini App.\n\n"
        "Выберите действие:",
        reply_markup=get_miniapp_access_keyboard(),
    )


@router.message(F.text == MENU_MINIAPP_ADD)
async def add_access_start(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Start adding Mini App access flow.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await state.update_data(action="add")
    await state.set_state(MiniAppAccessState.waiting_for_user_id)
    await message.answer(
        "➕ <b>Добавление доступа к Mini App</b>\n\n"
        "Введите Telegram ID пользователя:\n\n"
        "<i>Можно переслать сообщение от пользователя или ввести ID вручную</i>",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == MENU_MINIAPP_REMOVE)
async def remove_access_start(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Start removing Mini App access flow.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await state.update_data(action="remove")
    await state.set_state(MiniAppAccessState.waiting_for_user_id)
    await message.answer(
        "➖ <b>Удаление доступа к Mini App</b>\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == MENU_MINIAPP_EXTEND)
async def extend_access_start(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Start extending Mini App access flow.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    await state.update_data(action="extend")
    await state.set_state(MiniAppAccessState.waiting_for_user_id)
    await message.answer(
        "📅 <b>Продление доступа к Mini App</b>\n\n"
        "Введите Telegram ID пользователя:",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text == MENU_MINIAPP_LIST)
async def list_miniapp_access(message: Message, is_admin: bool = False) -> None:
    """List all Mini App access entries.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    if not is_admin:
        return

    async with async_session_maker() as session:
        result = await session.execute(
            select(MiniAppAccess).order_by(MiniAppAccess.created_at.desc()).limit(50)
        )
        access_list = result.scalars().all()

    if not access_list:
        await message.answer(
            "📋 <b>Список доступов Mini App пуст</b>\n\n"
            "Пока никто не добавлен.",
            reply_markup=get_miniapp_access_keyboard(),
        )
        return

    lines = ["📋 <b>Пользователи Mini App</b>\n"]

    for access in access_list:
        # Status icon
        if not access.is_active:
            status = "❌"
        elif access.access_type == "unlimited":
            status = "♾️"
        elif access.is_expired():
            status = "⏰"  # Expired
        else:
            status = "✅"

        # Build name display
        name_parts = []
        if access.first_name:
            name_parts.append(access.first_name)
        if access.username:
            name_parts.append(f"@{access.username}")
        name = " ".join(name_parts) if name_parts else "—"

        # Build expiration display
        if access.access_type == "unlimited":
            expires = "♾ бессрочно"
        elif access.expires_at:
            expires = f"до {access.expires_at.strftime('%d.%m.%Y')}"
            if access.is_expired():
                expires += " ⚠️"
        else:
            expires = "—"

        lines.append(f"{status} <code>{access.user_id}</code> | {name} | {expires}")

    lines.append("\n<i>Статусы: ✅ активен, ♾️ бессрочно, ⏰ истёк, ❌ отключён</i>")

    await message.answer("\n".join(lines), reply_markup=get_miniapp_access_keyboard())


@router.message(MiniAppAccessState.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext) -> None:
    """Process user ID input.

    Args:
        message: Incoming message
        state: FSM context
    """
    if message.text == MENU_BACK:
        await state.clear()
        await message.answer(
            "📱 <b>Управление Mini App</b>",
            reply_markup=get_miniapp_access_keyboard(),
        )
        return

    # Handle forwarded messages
    user_id = None
    username = None
    first_name = None

    if message.forward_from:
        user_id = message.forward_from.id
        username = message.forward_from.username
        first_name = message.forward_from.first_name
    else:
        try:
            user_id = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Введите корректный Telegram ID (число) или перешлите сообщение от пользователя.")
            return

    data = await state.get_data()
    action = data.get("action")

    if action == "add":
        # Check if already exists
        async with async_session_maker() as session:
            result = await session.execute(
                select(MiniAppAccess).where(MiniAppAccess.user_id == user_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                if existing.is_active:
                    await message.answer(
                        f"⚠️ Пользователь <code>{user_id}</code> уже имеет доступ к Mini App.\n\n"
                        f"Тип: {existing.access_type}\n"
                        f"Активен до: {existing.expires_at.strftime('%d.%m.%Y') if existing.expires_at else 'бессрочно'}",
                        reply_markup=get_miniapp_access_keyboard(),
                    )
                    await state.clear()
                    return
                else:
                    # Reactivate existing access
                    await state.update_data(user_id=user_id, reactivate=True, username=username, first_name=first_name)
            else:
                await state.update_data(user_id=user_id, reactivate=False, username=username, first_name=first_name)

        await state.set_state(MiniAppAccessState.waiting_for_access_type)
        await message.answer(
            f"Выберите тип доступа для пользователя <code>{user_id}</code>:",
            reply_markup=get_access_type_keyboard(),
        )

    elif action == "remove":
        async with async_session_maker() as session:
            result = await session.execute(
                select(MiniAppAccess).where(MiniAppAccess.user_id == user_id)
            )
            access = result.scalar_one_or_none()

            if not access:
                await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден в списке доступов.")
                await state.clear()
                await message.answer(
                    "📱 <b>Управление Mini App</b>",
                    reply_markup=get_miniapp_access_keyboard(),
                )
                return

            access.is_active = False
            access.updated_at = datetime.now(timezone.utc)
            await session.commit()

        await state.clear()
        await message.answer(
            f"✅ Доступ пользователя <code>{user_id}</code> к Mini App отключён.",
            reply_markup=get_miniapp_access_keyboard(),
        )

    elif action == "extend":
        async with async_session_maker() as session:
            result = await session.execute(
                select(MiniAppAccess).where(MiniAppAccess.user_id == user_id)
            )
            access = result.scalar_one_or_none()

            if not access:
                await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден в списке доступов.")
                await state.clear()
                await message.answer(
                    "📱 <b>Управление Mini App</b>",
                    reply_markup=get_miniapp_access_keyboard(),
                )
                return

            if access.access_type == "unlimited":
                await message.answer(
                    f"ℹ️ У пользователя <code>{user_id}</code> бессрочный доступ. Продление не требуется.",
                    reply_markup=get_miniapp_access_keyboard(),
                )
                await state.clear()
                return

        await state.update_data(user_id=user_id)
        await state.set_state(MiniAppAccessState.waiting_for_days)
        await message.answer(
            f"Введите количество дней для продления доступа пользователя <code>{user_id}</code>:",
            reply_markup=get_back_keyboard(),
        )


@router.message(MiniAppAccessState.waiting_for_access_type)
async def process_access_type(message: Message, state: FSMContext) -> None:
    """Process access type selection.

    Args:
        message: Incoming message
        state: FSM context
    """
    if message.text == MENU_BACK:
        await state.clear()
        await message.answer(
            "📱 <b>Управление Mini App</b>",
            reply_markup=get_miniapp_access_keyboard(),
        )
        return

    if message.text == MENU_MINIAPP_UNLIMITED:
        # Add unlimited access
        data = await state.get_data()
        user_id = data.get("user_id")
        reactivate = data.get("reactivate", False)
        username = data.get("username")
        first_name = data.get("first_name")
        admin_id = message.from_user.id

        async with async_session_maker() as session:
            if reactivate:
                result = await session.execute(
                    select(MiniAppAccess).where(MiniAppAccess.user_id == user_id)
                )
                access = result.scalar_one_or_none()
                access.is_active = True
                access.access_type = "unlimited"
                access.expires_at = None
                access.notified_2_days = False
                access.notified_1_day = False
                access.updated_at = datetime.now(timezone.utc)
                if username:
                    access.username = username
                if first_name:
                    access.first_name = first_name
            else:
                access = MiniAppAccess(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    access_type="unlimited",
                    expires_at=None,
                    is_active=True,
                    created_by=admin_id,
                )
                session.add(access)

            await session.commit()

        await state.clear()
        await message.answer(
            f"✅ Пользователю <code>{user_id}</code> предоставлен бессрочный доступ к Mini App.",
            reply_markup=get_miniapp_access_keyboard(),
        )

    elif message.text == MENU_MINIAPP_SUBSCRIPTION:
        await state.set_state(MiniAppAccessState.waiting_for_days)
        await message.answer(
            "Введите количество дней подписки:",
            reply_markup=get_back_keyboard(),
        )
    else:
        await message.answer(
            "Выберите тип доступа из предложенных вариантов.",
            reply_markup=get_access_type_keyboard(),
        )


@router.message(MiniAppAccessState.waiting_for_days)
async def process_days(message: Message, state: FSMContext) -> None:
    """Process days input.

    Args:
        message: Incoming message
        state: FSM context
    """
    if message.text == MENU_BACK:
        await state.clear()
        await message.answer(
            "📱 <b>Управление Mini App</b>",
            reply_markup=get_miniapp_access_keyboard(),
        )
        return

    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError("Days must be positive")
    except ValueError:
        await message.answer("❌ Введите корректное количество дней (положительное число).")
        return

    data = await state.get_data()
    action = data.get("action")
    user_id = data.get("user_id")
    admin_id = message.from_user.id

    expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    async with async_session_maker() as session:
        if action == "add":
            reactivate = data.get("reactivate", False)
            username = data.get("username")
            first_name = data.get("first_name")

            if reactivate:
                result = await session.execute(
                    select(MiniAppAccess).where(MiniAppAccess.user_id == user_id)
                )
                access = result.scalar_one_or_none()
                access.is_active = True
                access.access_type = "subscription"
                access.expires_at = expires_at
                access.notified_2_days = False
                access.notified_1_day = False
                access.updated_at = datetime.now(timezone.utc)
                if username:
                    access.username = username
                if first_name:
                    access.first_name = first_name
            else:
                access = MiniAppAccess(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    access_type="subscription",
                    expires_at=expires_at,
                    is_active=True,
                    created_by=admin_id,
                )
                session.add(access)

            await session.commit()

            await message.answer(
                f"✅ Пользователю <code>{user_id}</code> предоставлен доступ к Mini App.\n\n"
                f"Срок: {days} дней\n"
                f"Действует до: {expires_at.strftime('%d.%m.%Y %H:%M')} UTC",
            )

        elif action == "extend":
            result = await session.execute(
                select(MiniAppAccess).where(MiniAppAccess.user_id == user_id)
            )
            access = result.scalar_one_or_none()

            if access:
                # If current access is still valid, extend from current expiration
                if access.expires_at and access.expires_at > datetime.now(timezone.utc):
                    access.expires_at = access.expires_at + timedelta(days=days)
                else:
                    # Otherwise extend from now
                    access.expires_at = datetime.now(timezone.utc) + timedelta(days=days)

                access.is_active = True
                access.notified_2_days = False
                access.notified_1_day = False
                access.updated_at = datetime.now(timezone.utc)
                await session.commit()

                await message.answer(
                    f"✅ Доступ пользователя <code>{user_id}</code> продлён на {days} дней.\n\n"
                    f"Новая дата окончания: {access.expires_at.strftime('%d.%m.%Y %H:%M')} UTC",
                )

    await state.clear()
    await message.answer(
        "📱 <b>Управление Mini App</b>",
        reply_markup=get_miniapp_access_keyboard(),
    )

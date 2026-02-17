"""Strong Signal settings handler."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.strong_menu import get_strong_settings_keyboard
from services.strong_client import strong_client
from shared.constants import MENU_STRONG_SETTINGS
from states.navigation import MenuState

router = Router()


@router.message(MenuState.strong, F.text == MENU_STRONG_SETTINGS)
async def strong_settings_menu(message: Message, state: FSMContext) -> None:
    """Show Strong Signal settings."""
    await state.set_state(MenuState.strong_settings)
    user_id = message.from_user.id

    try:
        settings = await strong_client.get_user_settings(user_id)
    except Exception:
        settings = {
            "notifications_enabled": True,
            "long_signals": True,
            "short_signals": True,
        }

    await state.update_data(
        strong_notifications=settings.get("notifications_enabled", True),
        strong_long=settings.get("long_signals", True),
        strong_short=settings.get("short_signals", True),
    )

    await message.answer(
        "⚙️ <b>Настройки Strong Signal</b>\n\n"
        "Управляйте уведомлениями и фильтрами направлений:",
        reply_markup=get_strong_settings_keyboard(
            notifications_enabled=settings.get("notifications_enabled", True),
            long_enabled=settings.get("long_signals", True),
            short_enabled=settings.get("short_signals", True),
        ),
    )


@router.message(MenuState.strong_settings, F.text.contains("уведомления"))
async def toggle_notifications(message: Message, state: FSMContext) -> None:
    """Toggle Strong Signal notifications."""
    user_id = message.from_user.id
    data = await state.get_data()
    new_val = not data.get("strong_notifications", True)

    try:
        await strong_client.update_user_settings(
            user_id, {"notifications_enabled": new_val}
        )
        await state.update_data(strong_notifications=new_val)
        status = "включены ✅" if new_val else "выключены ❌"
        await message.answer(f"🔔 Уведомления Strong Signal {status}")
    except Exception:
        await message.answer("⚠️ Не удалось обновить настройки")

    await _refresh_settings(message, state)


@router.message(MenuState.strong_settings, F.text.endswith("Long"))
async def toggle_long(message: Message, state: FSMContext) -> None:
    """Toggle Long signal filter."""
    user_id = message.from_user.id
    data = await state.get_data()
    new_val = not data.get("strong_long", True)

    try:
        await strong_client.update_user_settings(user_id, {"long_signals": new_val})
        await state.update_data(strong_long=new_val)
        status = "включены ✅" if new_val else "выключены ❌"
        await message.answer(f"🧤 Long сигналы {status}")
    except Exception:
        await message.answer("⚠️ Не удалось обновить настройки")

    await _refresh_settings(message, state)


@router.message(MenuState.strong_settings, F.text.endswith("Short"))
async def toggle_short(message: Message, state: FSMContext) -> None:
    """Toggle Short signal filter."""
    user_id = message.from_user.id
    data = await state.get_data()
    new_val = not data.get("strong_short", True)

    try:
        await strong_client.update_user_settings(user_id, {"short_signals": new_val})
        await state.update_data(strong_short=new_val)
        status = "включены ✅" if new_val else "выключены ❌"
        await message.answer(f"🎒 Short сигналы {status}")
    except Exception:
        await message.answer("⚠️ Не удалось обновить настройки")

    await _refresh_settings(message, state)


async def _refresh_settings(message: Message, state: FSMContext) -> None:
    """Refresh settings keyboard."""
    data = await state.get_data()
    await message.answer(
        "Настройки:",
        reply_markup=get_strong_settings_keyboard(
            notifications_enabled=data.get("strong_notifications", True),
            long_enabled=data.get("strong_long", True),
            short_enabled=data.get("strong_short", True),
        ),
    )

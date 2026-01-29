"""Impulse activity settings handlers."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.reply.impulse_menu import (
    get_activity_menu_keyboard,
    get_impulse_menu_keyboard,
)
from keyboards.reply.back import get_back_keyboard
from services.impulse_client import impulse_client
from shared.constants import MENU_ACTIVITY, MENU_BACK
from states.navigation import MenuState

router = Router()


class ActivitySettingsState(StatesGroup):
    """States for activity settings."""

    waiting_for_window = State()
    waiting_for_threshold = State()


@router.message(F.text == MENU_ACTIVITY)
async def activity_menu(message: Message, state: FSMContext) -> None:
    """Handle activity menu button.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.impulse_activity)
    user_id = message.from_user.id

    try:
        settings = await impulse_client.get_user_settings(user_id)
        window = settings.get("activity_window_minutes", 15)
        threshold = settings.get("activity_threshold", 10)
    except Exception:
        window = 15
        threshold = 10

    await message.answer(
        "⚡ <b>Настройки активности</b>\n\n"
        "Получайте уведомления при высокой активности рынка.\n\n"
        f"⏱ <b>Окно:</b> {window} минут\n"
        f"📊 <b>Порог:</b> {threshold} импульсов\n\n"
        "Вы получите уведомление, когда за указанное время "
        "произойдёт указанное количество импульсов.",
        reply_markup=get_activity_menu_keyboard(window, threshold),
    )


@router.message(F.text.startswith("⏱"))
async def change_activity_window(message: Message, state: FSMContext) -> None:
    """Start changing activity window.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(ActivitySettingsState.waiting_for_window)
    await message.answer(
        "⏱ <b>Окно активности</b>\n\n"
        "Введите количество минут (от 5 до 60):",
        reply_markup=get_back_keyboard(),
    )


@router.message(F.text.startswith("📊"))
async def change_activity_threshold(message: Message, state: FSMContext) -> None:
    """Start changing activity threshold.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(ActivitySettingsState.waiting_for_threshold)
    await message.answer(
        "📊 <b>Порог активности</b>\n\n"
        "Введите количество импульсов (от 1 до 100):",
        reply_markup=get_back_keyboard(),
    )


@router.message(ActivitySettingsState.waiting_for_window)
async def process_window_input(message: Message, state: FSMContext) -> None:
    """Process activity window input.

    Args:
        message: Incoming message
        state: FSM context
    """
    try:
        value = int(message.text.strip())
        if not 5 <= value <= 60:
            raise ValueError("Out of range")

        user_id = message.from_user.id
        await impulse_client.update_user_settings(
            user_id, {"activity_window_minutes": value}
        )

        await state.clear()
        await message.answer(f"✅ Окно активности установлено: {value} минут")

        # Refresh menu
        settings = await impulse_client.get_user_settings(user_id)
        await message.answer(
            "⚡ <b>Настройки активности</b>",
            reply_markup=get_activity_menu_keyboard(
                settings.get("activity_window_minutes", 15),
                settings.get("activity_threshold", 10),
            ),
        )

    except ValueError:
        await message.answer(
            "❌ Введите число от 5 до 60.\n\nПопробуйте ещё раз:"
        )


@router.message(ActivitySettingsState.waiting_for_threshold)
async def process_threshold_input(message: Message, state: FSMContext) -> None:
    """Process activity threshold input.

    Args:
        message: Incoming message
        state: FSM context
    """
    try:
        value = int(message.text.strip())
        if not 1 <= value <= 100:
            raise ValueError("Out of range")

        user_id = message.from_user.id
        await impulse_client.update_user_settings(
            user_id, {"activity_threshold": value}
        )

        await state.clear()
        await message.answer(f"✅ Порог активности установлен: {value} импульсов")

        # Refresh menu
        settings = await impulse_client.get_user_settings(user_id)
        await message.answer(
            "⚡ <b>Настройки активности</b>",
            reply_markup=get_activity_menu_keyboard(
                settings.get("activity_window_minutes", 15),
                settings.get("activity_threshold", 10),
            ),
        )

    except ValueError:
        await message.answer(
            "❌ Введите число от 1 до 100.\n\nПопробуйте ещё раз:"
        )


@router.message(MenuState.impulse_activity, F.text == MENU_BACK)
async def back_from_activity(message: Message, state: FSMContext) -> None:
    """Handle back button from activity menu.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.impulse)
    await message.answer(
        "📊 <b>Раздел: Импульсы</b>",
        reply_markup=get_impulse_menu_keyboard(),
    )

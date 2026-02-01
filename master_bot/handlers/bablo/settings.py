"""Bablo settings handlers."""

import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.reply.bablo_menu import (
    get_bablo_menu_keyboard,
    get_bablo_settings_keyboard,
    get_settings_timeframe_keyboard,
    get_settings_direction_keyboard,
)
from keyboards.inline.bablo import get_quality_keyboard
from services.bablo_client import bablo_client
from shared.constants import MENU_BABLO_SETTINGS, MENU_BACK
from states.navigation import MenuState

router = Router()

# Timeframe mapping for settings
SETTINGS_TIMEFRAMES = ["1м", "5м", "15м", "30м", "1ч"]


def _parse_timeframes_from_settings(settings: dict) -> set[str]:
    """Parse enabled timeframes from settings dict.

    Args:
        settings: User settings dict

    Returns:
        Set of enabled timeframe strings
    """
    result = set()
    tf_map = {
        "timeframe_1m": "1м",
        "timeframe_5m": "5м",
        "timeframe_15m": "15м",
        "timeframe_30m": "30м",
        "timeframe_1h": "1ч",
    }
    for key, tf in tf_map.items():
        if settings.get(key, True):
            result.add(tf)
    return result


def _timeframes_to_settings(timeframes: set[str]) -> dict:
    """Convert timeframe set to settings dict.

    Args:
        timeframes: Set of timeframe strings

    Returns:
        Settings dict for API update
    """
    return {
        "timeframe_1m": "1м" in timeframes,
        "timeframe_5m": "5м" in timeframes,
        "timeframe_15m": "15м" in timeframes,
        "timeframe_30m": "30м" in timeframes,
        "timeframe_1h": "1ч" in timeframes,
    }


@router.message(MenuState.bablo, F.text == MENU_BABLO_SETTINGS)
async def bablo_settings_menu(message: Message, state: FSMContext) -> None:
    """Show Bablo settings menu.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_settings)
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)

        notifications = settings.get("notifications_enabled", True)
        min_quality = settings.get("min_quality", 7)
        long_signals = settings.get("long_signals", True)
        short_signals = settings.get("short_signals", True)

        status = "🔔 Включены" if notifications else "🔕 Выключены"

        # Directions
        directions = []
        if long_signals:
            directions.append("long")
        if short_signals:
            directions.append("short")

        # Timeframes
        timeframes = _parse_timeframes_from_settings(settings)
        tf_list = sorted(timeframes, key=lambda x: SETTINGS_TIMEFRAMES.index(x) if x in SETTINGS_TIMEFRAMES else 99)

        await message.answer(
            f"⚙️ <b>Настройки Bablo</b>\n\n"
            f"<i>Здесь настраивается фильтрация поступающих уведомлений о сигналах.</i>\n\n"
            f"Уведомления: {status}\n\n"
            f"⭐ <b>Мин. качество:</b> {min_quality}/10\n"
            f"⏱ <b>Таймфреймы:</b> {', '.join(tf_list) or 'все'}\n"
            f"📈 <b>Направления:</b> {', '.join(d.capitalize() for d in directions) or 'все'}\n\n"
            "Нажмите для изменения:",
            reply_markup=get_bablo_settings_keyboard(notifications, min_quality, tf_list or None, directions or None),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(MenuState.bablo_settings, F.text.in_(["🔔", "🔕", "🔔 Включить Bablo", "🔕 Выключить Bablo"]))
async def toggle_bablo_notifications(message: Message, state: FSMContext) -> None:
    """Toggle Bablo notifications.

    Args:
        message: Incoming message
        state: FSM context
    """
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)
        current = settings.get("notifications_enabled", True)
        new_value = not current

        await bablo_client.update_user_settings(user_id, {"notifications_enabled": new_value})

        if new_value:
            await message.answer("🔔 Уведомления Bablo <b>включены</b>")
        else:
            await message.answer(
                "🔕 Уведомления Bablo <b>выключены</b>\n\n"
                "<i>Вы будете получать только отчёты.</i>"
            )

        # Refresh settings menu
        min_quality = settings.get("min_quality", 7)
        long_signals = settings.get("long_signals", True)
        short_signals = settings.get("short_signals", True)
        directions = []
        if long_signals:
            directions.append("long")
        if short_signals:
            directions.append("short")
        timeframes = _parse_timeframes_from_settings(settings)
        tf_list = sorted(timeframes, key=lambda x: SETTINGS_TIMEFRAMES.index(x) if x in SETTINGS_TIMEFRAMES else 99)

        await message.answer(
            "Настройки Bablo:",
            reply_markup=get_bablo_settings_keyboard(new_value, min_quality, tf_list or None, directions or None),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(MenuState.bablo_settings, F.text.startswith("⭐"))
async def change_quality_threshold(message: Message) -> None:
    """Show quality threshold selection.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)
        current = settings.get("min_quality", 7)
    except Exception:
        current = 7

    await message.answer(
        "⭐ <b>Минимальное качество</b>\n\n"
        "Выберите минимальный показатель качества для уведомлений:",
        reply_markup=get_quality_keyboard(current),
    )


@router.callback_query(F.data.startswith("bablo:quality:"))
async def process_quality_callback(callback: CallbackQuery) -> None:
    """Process quality selection.

    Args:
        callback: Callback query
    """
    value = int(callback.data.split(":")[2])
    user_id = callback.from_user.id

    try:
        await bablo_client.update_user_settings(user_id, {"min_quality": value})
        await callback.answer(f"✅ Минимальное качество: {value}/10")

        await callback.message.edit_text(
            f"⭐ <b>Качество</b>\n\n"
            f"✅ Установлено: <b>{value}/10</b>\n\n"
            f"Вы будете получать только сигналы с качеством {value} и выше."
        )

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# Timeframe settings handlers
@router.message(MenuState.bablo_settings, F.text.startswith("⏱"))
async def open_timeframe_settings(message: Message, state: FSMContext) -> None:
    """Open timeframe selection for settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)
        timeframes = _parse_timeframes_from_settings(settings)
    except Exception:
        timeframes = set(SETTINGS_TIMEFRAMES)

    await state.set_state(MenuState.bablo_settings_timeframes)
    await state.update_data(selected_timeframes=timeframes)

    await message.answer(
        "⏱ <b>Таймфреймы для уведомлений</b>\n\n"
        "Выберите таймфреймы (можно несколько).\n\n"
        "Затем нажмите «Сохранить»",
        reply_markup=get_settings_timeframe_keyboard(timeframes),
    )


@router.message(MenuState.bablo_settings_timeframes, F.text.regexp(r"^[✅⬜] \d+[мч]$"))
async def toggle_settings_timeframe(message: Message, state: FSMContext) -> None:
    """Toggle timeframe in settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    match = re.search(r"(\d+[мч])$", message.text)
    if not match:
        return

    timeframe = match.group(1)
    data = await state.get_data()
    selected = data.get("selected_timeframes", set())

    if isinstance(selected, list):
        selected = set(selected)

    if timeframe in selected:
        selected.discard(timeframe)
        status_text = f"❌ {timeframe} таймфрейм снят"
    else:
        selected.add(timeframe)
        status_text = f"✅ {timeframe} таймфрейм"

    await state.update_data(selected_timeframes=selected)
    await message.answer(
        status_text,
        reply_markup=get_settings_timeframe_keyboard(selected),
    )


@router.message(MenuState.bablo_settings_timeframes, F.text == "✅ Сохранить")
async def save_timeframe_settings(message: Message, state: FSMContext) -> None:
    """Save timeframe settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    user_id = message.from_user.id
    data = await state.get_data()
    timeframes = data.get("selected_timeframes", set())

    if isinstance(timeframes, list):
        timeframes = set(timeframes)

    # If no timeframes selected, enable all
    if not timeframes:
        timeframes = set(SETTINGS_TIMEFRAMES)

    try:
        settings_update = _timeframes_to_settings(timeframes)
        await bablo_client.update_user_settings(user_id, settings_update)

        tf_list = sorted(timeframes, key=lambda x: SETTINGS_TIMEFRAMES.index(x) if x in SETTINGS_TIMEFRAMES else 99)
        await message.answer(
            f"✅ Таймфреймы сохранены: <b>{', '.join(tf_list)}</b>"
        )

        # Return to settings menu
        await state.set_state(MenuState.bablo_settings)
        settings = await bablo_client.get_user_settings(user_id)

        notifications = settings.get("notifications_enabled", True)
        min_quality = settings.get("min_quality", 7)
        long_signals = settings.get("long_signals", True)
        short_signals = settings.get("short_signals", True)
        directions = []
        if long_signals:
            directions.append("long")
        if short_signals:
            directions.append("short")

        await message.answer(
            "Настройки Bablo:",
            reply_markup=get_bablo_settings_keyboard(notifications, min_quality, tf_list or None, directions or None),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(MenuState.bablo_settings_timeframes, F.text == MENU_BACK)
async def back_from_timeframe_settings(message: Message, state: FSMContext) -> None:
    """Go back from timeframe settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_settings)
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)

        notifications = settings.get("notifications_enabled", True)
        min_quality = settings.get("min_quality", 7)
        long_signals = settings.get("long_signals", True)
        short_signals = settings.get("short_signals", True)
        directions = []
        if long_signals:
            directions.append("long")
        if short_signals:
            directions.append("short")
        timeframes = _parse_timeframes_from_settings(settings)
        tf_list = sorted(timeframes, key=lambda x: SETTINGS_TIMEFRAMES.index(x) if x in SETTINGS_TIMEFRAMES else 99)

        await message.answer(
            "Настройки Bablo:",
            reply_markup=get_bablo_settings_keyboard(notifications, min_quality, tf_list or None, directions or None),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


# Direction settings handlers
@router.message(MenuState.bablo_settings, F.text.startswith("📈"))
async def open_direction_settings(message: Message, state: FSMContext) -> None:
    """Open direction selection for settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)
        long_enabled = settings.get("long_signals", True)
        short_enabled = settings.get("short_signals", True)
    except Exception:
        long_enabled = True
        short_enabled = True

    await state.set_state(MenuState.bablo_settings_directions)
    await state.update_data(long_enabled=long_enabled, short_enabled=short_enabled)

    await message.answer(
        "📈 <b>Направления для уведомлений</b>\n\n"
        "Выберите направления сигналов:\n"
        "• Long — сигналы на рост\n"
        "• Short — сигналы на падение\n\n"
        "Можно выбрать оба. Затем нажмите «Сохранить»",
        reply_markup=get_settings_direction_keyboard(long_enabled, short_enabled),
    )


@router.message(MenuState.bablo_settings_directions, F.text.regexp(r"^[✅⬜] (Long|Short)$"))
async def toggle_settings_direction(message: Message, state: FSMContext) -> None:
    """Toggle direction in settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    data = await state.get_data()
    long_enabled = data.get("long_enabled", True)
    short_enabled = data.get("short_enabled", True)

    if "Long" in message.text:
        long_enabled = not long_enabled
    elif "Short" in message.text:
        short_enabled = not short_enabled

    await state.update_data(long_enabled=long_enabled, short_enabled=short_enabled)
    await message.answer(
        "Выберите направления:",
        reply_markup=get_settings_direction_keyboard(long_enabled, short_enabled),
    )


@router.message(MenuState.bablo_settings_directions, F.text == "✅ Сохранить")
async def save_direction_settings(message: Message, state: FSMContext) -> None:
    """Save direction settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    user_id = message.from_user.id
    data = await state.get_data()
    long_enabled = data.get("long_enabled", True)
    short_enabled = data.get("short_enabled", True)

    # At least one direction must be enabled
    if not long_enabled and not short_enabled:
        long_enabled = True
        short_enabled = True

    try:
        await bablo_client.update_user_settings(user_id, {
            "long_signals": long_enabled,
            "short_signals": short_enabled,
        })

        directions = []
        if long_enabled:
            directions.append("Long")
        if short_enabled:
            directions.append("Short")

        await message.answer(
            f"✅ Направления сохранены: <b>{', '.join(directions)}</b>"
        )

        # Return to settings menu
        await state.set_state(MenuState.bablo_settings)
        settings = await bablo_client.get_user_settings(user_id)

        notifications = settings.get("notifications_enabled", True)
        min_quality = settings.get("min_quality", 7)
        timeframes = _parse_timeframes_from_settings(settings)
        tf_list = sorted(timeframes, key=lambda x: SETTINGS_TIMEFRAMES.index(x) if x in SETTINGS_TIMEFRAMES else 99)

        dir_list = []
        if long_enabled:
            dir_list.append("long")
        if short_enabled:
            dir_list.append("short")

        await message.answer(
            "Настройки Bablo:",
            reply_markup=get_bablo_settings_keyboard(notifications, min_quality, tf_list or None, dir_list or None),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(MenuState.bablo_settings_directions, F.text == MENU_BACK)
async def back_from_direction_settings(message: Message, state: FSMContext) -> None:
    """Go back from direction settings.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_settings)
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)

        notifications = settings.get("notifications_enabled", True)
        min_quality = settings.get("min_quality", 7)
        long_signals = settings.get("long_signals", True)
        short_signals = settings.get("short_signals", True)
        directions = []
        if long_signals:
            directions.append("long")
        if short_signals:
            directions.append("short")
        timeframes = _parse_timeframes_from_settings(settings)
        tf_list = sorted(timeframes, key=lambda x: SETTINGS_TIMEFRAMES.index(x) if x in SETTINGS_TIMEFRAMES else 99)

        await message.answer(
            "Настройки Bablo:",
            reply_markup=get_bablo_settings_keyboard(notifications, min_quality, tf_list or None, directions or None),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(MenuState.bablo_settings, F.text == MENU_BACK)
async def back_from_settings(message: Message, state: FSMContext) -> None:
    """Go back from settings to Bablo menu.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo)
    await message.answer(
        "💰 <b>Bablo</b>\n\nВыберите раздел:",
        reply_markup=get_bablo_menu_keyboard(),
    )

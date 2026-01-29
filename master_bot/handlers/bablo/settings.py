"""Bablo settings handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.reply.bablo_menu import get_bablo_settings_keyboard
from keyboards.inline.bablo import (
    get_quality_keyboard,
    get_strength_keyboard,
)
from services.bablo_client import bablo_client
from shared.constants import MENU_BABLO_SETTINGS
from states.navigation import MenuState

router = Router()


@router.message(F.text == MENU_BABLO_SETTINGS)
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
        min_strength = settings.get("min_strength", 3)
        long_signals = settings.get("long_signals", True)
        short_signals = settings.get("short_signals", True)

        status = "🔔 Включены" if notifications else "🔕 Выключены"
        directions = []
        if long_signals:
            directions.append("Long")
        if short_signals:
            directions.append("Short")

        # Timeframes
        timeframes = []
        if settings.get("timeframe_1m"):
            timeframes.append("1m")
        if settings.get("timeframe_15m"):
            timeframes.append("15m")
        if settings.get("timeframe_1h"):
            timeframes.append("1h")
        if settings.get("timeframe_4h"):
            timeframes.append("4h")

        await message.answer(
            f"⚙️ <b>Настройки Bablo</b>\n\n"
            f"Уведомления: {status}\n\n"
            f"⭐ <b>Мин. качество:</b> {min_quality}/10\n"
            f"📊 <b>Мин. сила сигнала:</b> {min_strength}/5\n"
            f"📈 <b>Направления:</b> {', '.join(directions) or 'Нет'}\n"
            f"⏱ <b>Таймфреймы:</b> {', '.join(timeframes) or 'Нет'}\n\n"
            "Нажмите для изменения:",
            reply_markup=get_bablo_settings_keyboard(notifications, min_quality, min_strength),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text.in_(["🔔 Включить Bablo", "🔕 Выключить Bablo"]))
async def toggle_bablo_notifications(message: Message) -> None:
    """Toggle Bablo notifications.

    Args:
        message: Incoming message
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
        min_strength = settings.get("min_strength", 3)

        await message.answer(
            "Настройки Bablo:",
            reply_markup=get_bablo_settings_keyboard(new_value, min_quality, min_strength),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text.startswith("⭐ Качество:"))
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


@router.message(F.text.startswith("📊 Сила:"))
async def change_strength_threshold(message: Message) -> None:
    """Show strength threshold selection.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await bablo_client.get_user_settings(user_id)
        current = settings.get("min_strength", 3)
    except Exception:
        current = 3

    await message.answer(
        "📊 <b>Минимальная сила сигнала</b>\n\n"
        "Выберите минимальное количество квадратов (сила сигнала):",
        reply_markup=get_strength_keyboard(current),
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
            "Вы будете получать только сигналы с качеством {value} и выше."
        )

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("bablo:strength:"))
async def process_strength_callback(callback: CallbackQuery) -> None:
    """Process strength selection.

    Args:
        callback: Callback query
    """
    value = int(callback.data.split(":")[2])
    user_id = callback.from_user.id

    try:
        await bablo_client.update_user_settings(user_id, {"min_strength": value})
        await callback.answer(f"✅ Минимальная сила: {value}/5")

        squares = "🟩" * value
        await callback.message.edit_text(
            f"📊 <b>Сила сигнала</b>\n\n"
            f"✅ Установлено: <b>{value}/5</b> {squares}\n\n"
            "Вы будете получать только сигналы с силой {value} и выше."
        )

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

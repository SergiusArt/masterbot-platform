"""Impulse notifications settings handlers."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.reply.impulse_menu import get_notifications_menu_keyboard
from keyboards.inline.thresholds import (
    get_growth_threshold_keyboard,
    get_fall_threshold_keyboard,
)
from services.impulse_client import impulse_client
from shared.constants import MENU_NOTIFICATIONS

router = Router()


@router.message(F.text == MENU_NOTIFICATIONS)
async def notifications_menu(message: Message) -> None:
    """Handle notifications menu button.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await impulse_client.get_user_settings(user_id)
        growth = settings.get("growth_threshold", 20)
        fall = settings.get("fall_threshold", -15)
        notifications_enabled = settings.get("notifications_enabled", True)
    except Exception:
        growth = 20
        fall = -15
        notifications_enabled = True

    status_text = "🔔 <b>Включены</b>" if notifications_enabled else "🔕 <b>Выключены</b>"

    await message.answer(
        f"🔔 <b>Уведомления об импульсах</b>\n\n"
        f"Статус: {status_text}\n\n"
        f"📈 <b>Порог роста:</b> {growth}%\n"
        f"📉 <b>Порог падения:</b> {fall}%\n\n"
        "<i>Если вам нужны только отчёты без сигналов в реальном времени — "
        "выключите уведомления.</i>\n\n"
        "Нажмите на кнопку для изменения:",
        reply_markup=get_notifications_menu_keyboard(growth, fall, notifications_enabled),
    )


@router.message(F.text.in_(["🔔 Включить уведомления", "🔕 Выключить уведомления"]))
async def toggle_notifications(message: Message) -> None:
    """Toggle notifications on/off.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await impulse_client.get_user_settings(user_id)
        current = settings.get("notifications_enabled", True)
        new_value = not current

        await impulse_client.update_user_settings(user_id, {"notifications_enabled": new_value})

        if new_value:
            await message.answer("🔔 Уведомления об импульсах <b>включены</b>")
        else:
            await message.answer(
                "🔕 Уведомления об импульсах <b>выключены</b>\n\n"
                "<i>Вы будете получать только отчёты.</i>"
            )

        # Refresh menu
        growth = settings.get("growth_threshold", 20)
        fall = settings.get("fall_threshold", -15)

        await message.answer(
            "Настройки уведомлений:",
            reply_markup=get_notifications_menu_keyboard(growth, fall, new_value),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text.startswith("📈 Рост:"))
async def change_growth_threshold(message: Message) -> None:
    """Show growth threshold selection.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await impulse_client.get_user_settings(user_id)
        current = settings.get("growth_threshold", 20)
    except Exception:
        current = 20

    await message.answer(
        "📈 <b>Порог роста</b>\n\n"
        "Выберите процент, при котором будете получать уведомления о росте:",
        reply_markup=get_growth_threshold_keyboard(current),
    )


@router.message(F.text.startswith("📉 Падение:"))
async def change_fall_threshold(message: Message) -> None:
    """Show fall threshold selection.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await impulse_client.get_user_settings(user_id)
        current = settings.get("fall_threshold", -15)
    except Exception:
        current = -15

    await message.answer(
        "📉 <b>Порог падения</b>\n\n"
        "Выберите процент, при котором будете получать уведомления о падении:",
        reply_markup=get_fall_threshold_keyboard(current),
    )


@router.callback_query(F.data.startswith("threshold:"))
async def process_threshold_callback(callback: CallbackQuery) -> None:
    """Process threshold selection callback.

    Args:
        callback: Callback query
    """
    _, threshold_type, value = callback.data.split(":")
    value = int(value)
    user_id = callback.from_user.id

    try:
        setting_name = f"{threshold_type}_threshold"
        await impulse_client.update_user_settings(user_id, {setting_name: value})

        await callback.answer(f"✅ Порог установлен: {value}%")

        # Update message
        settings = await impulse_client.get_user_settings(user_id)
        growth = settings.get("growth_threshold", 20)
        fall = settings.get("fall_threshold", -15)

        await callback.message.edit_text(
            "🔔 <b>Уведомления</b>\n\n"
            f"📈 <b>Порог роста:</b> {growth}%\n"
            f"📉 <b>Порог падения:</b> {fall}%\n\n"
            "✅ Настройки сохранены!"
        )

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

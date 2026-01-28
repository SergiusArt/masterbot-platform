"""Impulse reports handlers."""

from aiogram import Router, F
from aiogram.types import Message

from keyboards.reply.impulse_menu import get_reports_menu_keyboard
from services.impulse_client import impulse_client
from shared.constants import (
    MENU_REPORTS,
    MENU_MORNING_REPORT,
    MENU_EVENING_REPORT,
    MENU_WEEKLY_REPORT,
    MENU_MONTHLY_REPORT,
)

router = Router()


@router.message(F.text == MENU_REPORTS)
async def reports_menu(message: Message) -> None:
    """Handle reports menu button.

    Args:
        message: Incoming message
    """
    user_id = message.from_user.id

    try:
        settings = await impulse_client.get_user_settings(user_id)
        await message.answer(
            "📋 <b>Отчёты</b>\n\n"
            "Нажмите на кнопку, чтобы включить/выключить отчёт:",
            reply_markup=get_reports_menu_keyboard(
                morning=settings.get("morning_report", True),
                evening=settings.get("evening_report", True),
                weekly=settings.get("weekly_report", True),
                monthly=settings.get("monthly_report", True),
            ),
        )
    except Exception:
        await message.answer(
            "📋 <b>Отчёты</b>\n\n"
            "Нажмите на кнопку, чтобы включить/выключить отчёт:",
            reply_markup=get_reports_menu_keyboard(),
        )


@router.message(F.text.startswith(MENU_MORNING_REPORT))
async def toggle_morning_report(message: Message) -> None:
    """Toggle morning report setting.

    Args:
        message: Incoming message
    """
    await _toggle_report(message, "morning_report", "Утренний отчёт")


@router.message(F.text.startswith(MENU_EVENING_REPORT))
async def toggle_evening_report(message: Message) -> None:
    """Toggle evening report setting.

    Args:
        message: Incoming message
    """
    await _toggle_report(message, "evening_report", "Вечерний отчёт")


@router.message(F.text.startswith(MENU_WEEKLY_REPORT))
async def toggle_weekly_report(message: Message) -> None:
    """Toggle weekly report setting.

    Args:
        message: Incoming message
    """
    await _toggle_report(message, "weekly_report", "Недельный отчёт")


@router.message(F.text.startswith(MENU_MONTHLY_REPORT))
async def toggle_monthly_report(message: Message) -> None:
    """Toggle monthly report setting.

    Args:
        message: Incoming message
    """
    await _toggle_report(message, "monthly_report", "Месячный отчёт")


async def _toggle_report(message: Message, setting: str, name: str) -> None:
    """Toggle report setting.

    Args:
        message: Incoming message
        setting: Setting name
        name: Human-readable name
    """
    user_id = message.from_user.id

    try:
        # Get current settings
        settings = await impulse_client.get_user_settings(user_id)
        current_value = settings.get(setting, True)

        # Toggle value
        new_value = not current_value
        await impulse_client.update_user_settings(user_id, {setting: new_value})

        status = "включён ✅" if new_value else "выключен ❌"
        await message.answer(f"📋 {name} {status}")

        # Refresh menu
        settings[setting] = new_value
        await message.answer(
            "Выберите отчёт для настройки:",
            reply_markup=get_reports_menu_keyboard(
                morning=settings.get("morning_report", True),
                evening=settings.get("evening_report", True),
                weekly=settings.get("weekly_report", True),
                monthly=settings.get("monthly_report", True),
            ),
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

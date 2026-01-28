"""General settings handlers."""

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from keyboards.reply.main_menu import get_main_menu_keyboard
from shared.constants import MENU_SETTINGS, MENU_BACK

router = Router()


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """Build settings menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌍 Часовой пояс")],
            [KeyboardButton(text="🌐 Язык")],
            [KeyboardButton(text=MENU_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


@router.message(F.text == MENU_SETTINGS)
async def settings_menu(message: Message) -> None:
    """Handle settings menu button.

    Args:
        message: Incoming message
    """
    await message.answer(
        "⚙️ <b>Настройки</b>\n\nВыберите раздел:",
        reply_markup=get_settings_keyboard(),
    )


@router.message(F.text == "🌍 Часовой пояс")
async def timezone_settings(message: Message) -> None:
    """Handle timezone settings.

    Args:
        message: Incoming message
    """
    await message.answer(
        "🌍 <b>Часовой пояс</b>\n\n"
        "Текущий часовой пояс: <b>Europe/Moscow (UTC+3)</b>\n\n"
        "Для изменения часового пояса обратитесь к администратору."
    )


@router.message(F.text == "🌐 Язык")
async def language_settings(message: Message) -> None:
    """Handle language settings.

    Args:
        message: Incoming message
    """
    await message.answer(
        "🌐 <b>Язык</b>\n\n"
        "Текущий язык: <b>Русский</b>\n\n"
        "В данный момент поддерживается только русский язык."
    )

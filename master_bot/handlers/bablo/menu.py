"""Bablo section menu handler."""

from aiogram import Router, F
from aiogram.types import Message

from keyboards.reply.bablo_menu import get_bablo_menu_keyboard
from shared.constants import MENU_BABLO

router = Router()


@router.message(F.text == MENU_BABLO)
async def bablo_menu(message: Message) -> None:
    """Handle Bablo menu button.

    Args:
        message: Incoming message
    """
    await message.answer(
        "💰 <b>Раздел: Bablo</b>\n\n"
        "Торговые сигналы с вероятностным анализом.\n\n"
        "📊 <b>Статистика</b> — аналитика сигналов\n"
        "📋 <b>Сигналы</b> — последние сигналы\n"
        "⚙️ <b>Настройки</b> — фильтры уведомлений\n\n"
        "Выберите действие:",
        reply_markup=get_bablo_menu_keyboard(),
    )

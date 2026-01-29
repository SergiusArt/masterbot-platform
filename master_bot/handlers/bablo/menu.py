"""Bablo section menu handler."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.bablo_menu import get_bablo_menu_keyboard
from shared.constants import MENU_BABLO, MENU_BACK
from states.navigation import MenuState

router = Router()


@router.message(F.text == MENU_BABLO)
async def bablo_menu(message: Message, state: FSMContext) -> None:
    """Handle Bablo menu button.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo)
    await message.answer(
        "💰 <b>Раздел: Bablo</b>\n\n"
        "Торговые сигналы с вероятностным анализом.\n\n"
        "📊 <b>Статистика</b> — аналитика сигналов\n"
        "📋 <b>Сигналы</b> — последние сигналы\n"
        "⚙️ <b>Настройки</b> — фильтры уведомлений\n\n"
        "Выберите действие:",
        reply_markup=get_bablo_menu_keyboard(),
    )


@router.message(MenuState.bablo_analytics, F.text == MENU_BACK)
@router.message(MenuState.bablo_signals, F.text == MENU_BACK)
@router.message(MenuState.bablo_settings, F.text == MENU_BACK)
async def back_to_bablo_menu(message: Message, state: FSMContext) -> None:
    """Handle back button from Bablo sub-menus.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo)
    await message.answer(
        "💰 <b>Раздел: Bablo</b>\n\nВыберите действие:",
        reply_markup=get_bablo_menu_keyboard(),
    )

"""Impulse section menu handler."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.impulse_menu import get_impulse_menu_keyboard
from shared.constants import MENU_IMPULSES, EMOJI_CHART, animated
from states.navigation import MenuState

router = Router()


@router.message(F.text == MENU_IMPULSES)
async def impulse_menu(message: Message, state: FSMContext) -> None:
    """Handle impulse menu button.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.impulse)
    await message.answer(
        f"{animated(EMOJI_CHART, '📊')} <b>Раздел: Импульсы</b>\n\n"
        "Здесь вы можете просматривать аналитику по криптовалютам, "
        "настраивать уведомления и получать отчёты.\n\n"
        "Выберите действие:",
        reply_markup=get_impulse_menu_keyboard(),
    )

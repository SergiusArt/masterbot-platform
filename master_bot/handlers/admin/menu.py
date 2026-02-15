"""Admin panel menu handler."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.admin_menu import get_admin_menu_keyboard
from shared.constants import MENU_ADMIN, EMOJI_CROWN, animated
from states.navigation import MenuState

router = Router()


@router.message(F.text == MENU_ADMIN)
async def admin_menu(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Handle admin menu button.

    Args:
        message: Incoming message
        state: FSM context
        is_admin: Whether user is admin
    """
    if not is_admin:
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return

    await state.set_state(MenuState.admin)
    await message.answer(
        f"{animated(EMOJI_CROWN, '👑')} <b>Админ-панель</b>\n\n"
        "Управление платформой MasterBot.\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_menu_keyboard(),
    )

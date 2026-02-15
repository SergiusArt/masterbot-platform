"""Navigation handlers for menu transitions."""

from aiogram import Router, F
from aiogram.types import Message

from keyboards.reply.main_menu import get_main_menu_keyboard
from shared.constants import MENU_MAIN, EMOJI_HOME, animated

router = Router()


@router.message(F.text == MENU_MAIN)
async def back_to_main_menu(message: Message, is_admin: bool = False) -> None:
    """Handle return to main menu.

    Args:
        message: Incoming message
        is_admin: Whether user is admin
    """
    await message.answer(
        f"{animated(EMOJI_HOME, '🏠')} <b>Главное меню</b>\n\nВыберите раздел:",
        reply_markup=get_main_menu_keyboard(is_admin),
    )

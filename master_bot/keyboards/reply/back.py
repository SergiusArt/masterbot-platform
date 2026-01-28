"""Back button keyboard builder."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import MENU_BACK


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Build keyboard with only back button.

    Returns:
        Back button keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=MENU_BACK)]],
        resize_keyboard=True,
        is_persistent=True,
    )

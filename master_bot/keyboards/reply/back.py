"""Back button keyboard builder."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import MENU_BACK, MENU_MAIN


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Build keyboard with back and main menu buttons.

    Returns:
        Back button keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

"""Main menu keyboard builder."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_IMPULSES,
    MENU_BABLO,
    MENU_REPORTS,
    MENU_SETTINGS,
    MENU_ADMIN,
)


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Build main menu keyboard.

    Args:
        is_admin: Whether user is admin

    Returns:
        Main menu keyboard
    """
    buttons = [
        [KeyboardButton(text=MENU_IMPULSES), KeyboardButton(text=MENU_BABLO)],
        [KeyboardButton(text=MENU_REPORTS)],
        [KeyboardButton(text=MENU_SETTINGS)],
    ]

    if is_admin:
        buttons.append([KeyboardButton(text=MENU_ADMIN)])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True,
    )

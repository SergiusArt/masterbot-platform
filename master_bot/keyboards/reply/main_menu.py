"""Main menu keyboard builder."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_IMPULSES,
    MENU_BABLO,
    MENU_REPORTS,
    MENU_SETTINGS,
    MENU_ADMIN,
    EMOJI_CHART,
    EMOJI_MONEY,
    EMOJI_MEMO,
    EMOJI_TOOLBOX,
    EMOJI_CROWN,
)


def get_main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Build main menu keyboard.

    Args:
        is_admin: Whether user is admin

    Returns:
        Main menu keyboard
    """
    buttons = [
        [
            KeyboardButton(text=MENU_IMPULSES, style="primary", icon_custom_emoji_id=EMOJI_CHART),
            KeyboardButton(text=MENU_BABLO, style="success", icon_custom_emoji_id=EMOJI_MONEY),
        ],
        [KeyboardButton(text=MENU_REPORTS, icon_custom_emoji_id=EMOJI_MEMO)],
        [KeyboardButton(text=MENU_SETTINGS, icon_custom_emoji_id=EMOJI_TOOLBOX)],
    ]

    if is_admin:
        buttons.append([KeyboardButton(text=MENU_ADMIN, style="danger", icon_custom_emoji_id=EMOJI_CROWN)])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        is_persistent=True,
    )

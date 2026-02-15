"""Admin panel keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_MAIN,
    MENU_BACK,
    MENU_USERS,
    MENU_SERVICES,
    MENU_ADD_USER,
    MENU_REMOVE_USER,
    MENU_EXTEND_ACCESS,
    MENU_USER_LIST,
    MENU_SERVICE_STATUS,
    MENU_RESTART_SERVICE,
    EMOJI_PERSON,
    EMOJI_TOOLBOX,
    EMOJI_HOME,
    EMOJI_PLUS,
    EMOJI_MINUS,
    EMOJI_CALENDAR,
    EMOJI_MEMO,
    EMOJI_SEARCH,
    EMOJI_REFRESH,
)


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build admin panel menu keyboard.

    Returns:
        Admin menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_USERS, style="primary", icon_custom_emoji_id=EMOJI_PERSON)],
            [KeyboardButton(text=MENU_SERVICES, style="primary", icon_custom_emoji_id=EMOJI_TOOLBOX)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_admin_users_keyboard() -> ReplyKeyboardMarkup:
    """Build admin users management keyboard.

    Returns:
        Admin users keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_ADD_USER, style="success", icon_custom_emoji_id=EMOJI_PLUS),
                KeyboardButton(text=MENU_REMOVE_USER, style="danger", icon_custom_emoji_id=EMOJI_MINUS),
            ],
            [
                KeyboardButton(text=MENU_EXTEND_ACCESS, style="primary", icon_custom_emoji_id=EMOJI_CALENDAR),
                KeyboardButton(text=MENU_USER_LIST, icon_custom_emoji_id=EMOJI_MEMO),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_admin_services_keyboard() -> ReplyKeyboardMarkup:
    """Build admin services management keyboard.

    Returns:
        Admin services keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_SERVICE_STATUS, style="primary", icon_custom_emoji_id=EMOJI_SEARCH)],
            [KeyboardButton(text=MENU_RESTART_SERVICE, style="danger", icon_custom_emoji_id=EMOJI_REFRESH)],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

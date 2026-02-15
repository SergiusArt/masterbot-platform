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
)


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build admin panel menu keyboard.

    Returns:
        Admin menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_USERS, style="primary")],
            [KeyboardButton(text=MENU_SERVICES, style="primary")],
            [KeyboardButton(text=MENU_MAIN)],
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
                KeyboardButton(text=MENU_ADD_USER, style="success"),
                KeyboardButton(text=MENU_REMOVE_USER, style="danger"),
            ],
            [
                KeyboardButton(text=MENU_EXTEND_ACCESS, style="primary"),
                KeyboardButton(text=MENU_USER_LIST),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
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
            [KeyboardButton(text=MENU_SERVICE_STATUS, style="primary")],
            [KeyboardButton(text=MENU_RESTART_SERVICE, style="danger")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

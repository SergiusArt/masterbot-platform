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
    MENU_MINIAPP,
    MENU_MINIAPP_ADD,
    MENU_MINIAPP_REMOVE,
    MENU_MINIAPP_EXTEND,
    MENU_MINIAPP_LIST,
    MENU_MINIAPP_UNLIMITED,
    MENU_MINIAPP_SUBSCRIPTION,
)


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build admin panel menu keyboard.

    Returns:
        Admin menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_USERS)],
            [KeyboardButton(text=MENU_MINIAPP)],
            [KeyboardButton(text=MENU_SERVICES)],
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
                KeyboardButton(text=MENU_ADD_USER),
                KeyboardButton(text=MENU_REMOVE_USER),
            ],
            [
                KeyboardButton(text=MENU_EXTEND_ACCESS),
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
            [KeyboardButton(text=MENU_SERVICE_STATUS)],
            [KeyboardButton(text=MENU_RESTART_SERVICE)],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_miniapp_access_keyboard() -> ReplyKeyboardMarkup:
    """Build Mini App access management keyboard.

    Returns:
        Mini App access keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_MINIAPP_ADD),
                KeyboardButton(text=MENU_MINIAPP_REMOVE),
            ],
            [
                KeyboardButton(text=MENU_MINIAPP_EXTEND),
                KeyboardButton(text=MENU_MINIAPP_LIST),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_access_type_keyboard() -> ReplyKeyboardMarkup:
    """Build access type selection keyboard.

    Returns:
        Access type keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_MINIAPP_UNLIMITED),
                KeyboardButton(text=MENU_MINIAPP_SUBSCRIPTION),
            ],
            [KeyboardButton(text=MENU_BACK)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

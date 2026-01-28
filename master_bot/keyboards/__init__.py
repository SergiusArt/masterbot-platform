"""Keyboard builders for Master Bot."""

from keyboards.reply.main_menu import get_main_menu_keyboard
from keyboards.reply.impulse_menu import (
    get_impulse_menu_keyboard,
    get_analytics_menu_keyboard,
    get_notifications_menu_keyboard,
    get_reports_menu_keyboard,
    get_activity_menu_keyboard,
)
from keyboards.reply.admin_menu import (
    get_admin_menu_keyboard,
    get_admin_users_keyboard,
    get_admin_services_keyboard,
)
from keyboards.reply.back import get_back_keyboard

__all__ = [
    "get_main_menu_keyboard",
    "get_impulse_menu_keyboard",
    "get_analytics_menu_keyboard",
    "get_notifications_menu_keyboard",
    "get_reports_menu_keyboard",
    "get_activity_menu_keyboard",
    "get_admin_menu_keyboard",
    "get_admin_users_keyboard",
    "get_admin_services_keyboard",
    "get_back_keyboard",
]

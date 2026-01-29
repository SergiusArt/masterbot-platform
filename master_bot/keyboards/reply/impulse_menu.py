"""Impulse section keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_MAIN,
    MENU_BACK,
    MENU_ANALYTICS,
    MENU_NOTIFICATIONS,
    MENU_ACTIVITY,
    MENU_TODAY,
    MENU_YESTERDAY,
    MENU_WEEK,
    MENU_MONTH,
    MENU_MORNING_REPORT,
    MENU_EVENING_REPORT,
    MENU_WEEKLY_REPORT,
    MENU_MONTHLY_REPORT,
)


def get_impulse_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build impulse section menu keyboard.

    Returns:
        Impulse menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_ANALYTICS),
                KeyboardButton(text=MENU_NOTIFICATIONS),
            ],
            [
                KeyboardButton(text=MENU_ACTIVITY),
            ],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_analytics_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build analytics period selection keyboard.

    Returns:
        Analytics menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_TODAY),
                KeyboardButton(text=MENU_YESTERDAY),
            ],
            [
                KeyboardButton(text=MENU_WEEK),
                KeyboardButton(text=MENU_MONTH),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_notifications_menu_keyboard(
    growth_threshold: int = 20,
    fall_threshold: int = -15,
    notifications_enabled: bool = True,
) -> ReplyKeyboardMarkup:
    """Build notifications settings keyboard.

    Args:
        growth_threshold: Current growth threshold
        fall_threshold: Current fall threshold
        notifications_enabled: Whether notifications are enabled

    Returns:
        Notifications menu keyboard
    """
    toggle_text = "🔕 Выключить уведомления" if notifications_enabled else "🔔 Включить уведомления"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=toggle_text)],
            [KeyboardButton(text=f"📈 Рост: {growth_threshold}%")],
            [KeyboardButton(text=f"📉 Падение: {fall_threshold}%")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_reports_menu_keyboard(
    morning: bool = True,
    evening: bool = True,
    weekly: bool = True,
    monthly: bool = True,
) -> ReplyKeyboardMarkup:
    """Build reports settings keyboard.

    Args:
        morning: Morning report enabled
        evening: Evening report enabled
        weekly: Weekly report enabled
        monthly: Monthly report enabled

    Returns:
        Reports menu keyboard
    """

    def status(enabled: bool) -> str:
        return "✅" if enabled else "❌"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=f"{MENU_MORNING_REPORT}: {status(morning)}"),
                KeyboardButton(text=f"{MENU_EVENING_REPORT}: {status(evening)}"),
            ],
            [
                KeyboardButton(text=f"{MENU_WEEKLY_REPORT}: {status(weekly)}"),
                KeyboardButton(text=f"{MENU_MONTHLY_REPORT}: {status(monthly)}"),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_activity_menu_keyboard(
    window: int = 15,
    threshold: int = 10,
) -> ReplyKeyboardMarkup:
    """Build activity settings keyboard.

    Args:
        window: Activity window in minutes
        threshold: Activity threshold

    Returns:
        Activity menu keyboard
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"⏱ Окно: {window} мин")],
            [KeyboardButton(text=f"📊 Порог: {threshold}")],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

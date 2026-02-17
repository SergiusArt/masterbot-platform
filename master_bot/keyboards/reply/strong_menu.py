"""Strong Signal section keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from shared.constants import (
    MENU_MAIN,
    MENU_BACK,
    MENU_STRONG_SIGNALS,
    MENU_STRONG_SETTINGS,
    EMOJI_MEMO,
    EMOJI_TOOLBOX,
    EMOJI_HOME,
)

# Period button constants
BTN_STRONG_WEEK = "За неделю"
BTN_STRONG_MONTH = "За месяц"
BTN_STRONG_PREV_MONTH = "За прошлый месяц"


def get_strong_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build Strong Signal section menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=MENU_STRONG_SIGNALS, style="primary", icon_custom_emoji_id=EMOJI_MEMO),
                KeyboardButton(text=MENU_STRONG_SETTINGS, icon_custom_emoji_id=EMOJI_TOOLBOX),
            ],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_strong_signals_keyboard() -> ReplyKeyboardMarkup:
    """Build Strong Signal period selection keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=BTN_STRONG_WEEK, style="primary"),
                KeyboardButton(text=BTN_STRONG_MONTH, style="primary"),
            ],
            [KeyboardButton(text=BTN_STRONG_PREV_MONTH)],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def get_strong_settings_keyboard(
    notifications_enabled: bool = True,
    long_enabled: bool = True,
    short_enabled: bool = True,
) -> ReplyKeyboardMarkup:
    """Build Strong Signal settings keyboard."""
    if notifications_enabled:
        toggle_text = "🔕 Выключить уведомления"
        toggle_style = "danger"
    else:
        toggle_text = "🔔 Включить уведомления"
        toggle_style = "success"

    long_check = "✅" if long_enabled else "⬜"
    short_check = "✅" if short_enabled else "⬜"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=toggle_text, style=toggle_style)],
            [
                KeyboardButton(text=f"{long_check} Long", style="success" if long_enabled else None),
                KeyboardButton(text=f"{short_check} Short", style="danger" if short_enabled else None),
            ],
            [KeyboardButton(text=MENU_BACK)],
            [KeyboardButton(text=MENU_MAIN, icon_custom_emoji_id=EMOJI_HOME)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

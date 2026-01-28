"""Bablo inline keyboards."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_quality_keyboard(current: int = 7) -> InlineKeyboardMarkup:
    """Build quality threshold selection keyboard.

    Args:
        current: Current quality threshold

    Returns:
        Quality selection inline keyboard
    """
    buttons = []
    for value in [5, 6, 7, 8, 9]:
        style = "✓ " if value == current else ""
        buttons.append(
            InlineKeyboardButton(
                text=f"{style}{value}/10",
                callback_data=f"bablo:quality:{value}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[:3],
            buttons[3:],
        ]
    )


def get_strength_keyboard(current: int = 3) -> InlineKeyboardMarkup:
    """Build strength threshold selection keyboard.

    Args:
        current: Current strength threshold

    Returns:
        Strength selection inline keyboard
    """
    buttons = []
    for value in [1, 2, 3, 4, 5]:
        style = "✓ " if value == current else ""
        squares = "🟩" * value
        buttons.append(
            InlineKeyboardButton(
                text=f"{style}{squares}",
                callback_data=f"bablo:strength:{value}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[:3],
            buttons[3:],
        ]
    )


def get_timeframe_keyboard(settings: dict) -> InlineKeyboardMarkup:
    """Build timeframe selection keyboard.

    Args:
        settings: User settings dict

    Returns:
        Timeframe selection inline keyboard
    """
    timeframes = [
        ("1m", "timeframe_1m"),
        ("15m", "timeframe_15m"),
        ("1h", "timeframe_1h"),
        ("4h", "timeframe_4h"),
    ]

    buttons = []
    for tf_label, tf_key in timeframes:
        enabled = settings.get(tf_key, True)
        status = "✅" if enabled else "❌"
        buttons.append(
            InlineKeyboardButton(
                text=f"{status} {tf_label}",
                callback_data=f"bablo:timeframe:{tf_key}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            buttons[:2],
            buttons[2:],
        ]
    )

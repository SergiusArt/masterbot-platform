"""Threshold selection inline keyboard."""

from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_threshold_keyboard(
    threshold_type: str,
    values: List[int],
    current: int,
) -> InlineKeyboardMarkup:
    """Build threshold selection inline keyboard.

    Args:
        threshold_type: Type of threshold (growth/fall)
        values: Available threshold values
        current: Current threshold value

    Returns:
        Threshold selection keyboard
    """
    buttons = []
    row = []

    for value in values:
        is_selected = value == current
        text = f"{'✅ ' if is_selected else ''}{value}%"
        callback_data = f"threshold:{threshold_type}:{value}"
        row.append(InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            style="success" if is_selected else None,
        ))

        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_growth_threshold_keyboard(current: int = 20) -> InlineKeyboardMarkup:
    """Build growth threshold keyboard.

    Args:
        current: Current growth threshold

    Returns:
        Growth threshold keyboard
    """
    values = [10, 15, 20, 25, 30, 50]
    return get_threshold_keyboard("growth", values, current)


def get_fall_threshold_keyboard(current: int = -15) -> InlineKeyboardMarkup:
    """Build fall threshold keyboard.

    Args:
        current: Current fall threshold

    Returns:
        Fall threshold keyboard
    """
    values = [-10, -15, -20, -25, -30, -50]
    return get_threshold_keyboard("fall", values, current)

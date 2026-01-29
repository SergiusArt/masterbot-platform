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

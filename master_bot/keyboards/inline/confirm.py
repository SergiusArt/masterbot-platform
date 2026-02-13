"""Confirmation inline keyboard."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_confirm_keyboard(
    action: str,
    confirm_text: str = "✅ Да",
    cancel_text: str = "❌ Нет",
) -> InlineKeyboardMarkup:
    """Build confirmation inline keyboard.

    Args:
        action: Action identifier for callback data
        confirm_text: Confirm button text
        cancel_text: Cancel button text

    Returns:
        Confirmation keyboard
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=confirm_text,
                    callback_data=f"confirm:{action}:yes",
                    style="success",
                ),
                InlineKeyboardButton(
                    text=cancel_text,
                    callback_data=f"confirm:{action}:no",
                    style="danger",
                ),
            ]
        ]
    )

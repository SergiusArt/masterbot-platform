"""Period selection inline keyboard."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_period_keyboard(prefix: str = "period") -> InlineKeyboardMarkup:
    """Build period selection inline keyboard.

    Args:
        prefix: Callback data prefix

    Returns:
        Period selection keyboard
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📅 Сегодня",
                    callback_data=f"{prefix}:today",
                ),
                InlineKeyboardButton(
                    text="📅 Вчера",
                    callback_data=f"{prefix}:yesterday",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Неделя",
                    callback_data=f"{prefix}:week",
                ),
                InlineKeyboardButton(
                    text="📅 Месяц",
                    callback_data=f"{prefix}:month",
                ),
            ],
        ]
    )

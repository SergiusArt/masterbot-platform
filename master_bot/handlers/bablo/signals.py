"""Bablo signals handlers."""

from aiogram import Router, F
from aiogram.types import Message

from keyboards.reply.bablo_menu import get_bablo_signals_keyboard, get_bablo_menu_keyboard
from services.bablo_client import bablo_client
from shared.constants import MENU_BABLO_SIGNALS, MENU_BACK

router = Router()


@router.message(F.text == MENU_BABLO_SIGNALS)
async def bablo_signals_menu(message: Message) -> None:
    """Handle Bablo signals menu.

    Args:
        message: Incoming message
    """
    await message.answer(
        "📋 <b>Сигналы Bablo</b>\n\n"
        "Выберите тип сигналов:",
        reply_markup=get_bablo_signals_keyboard(),
    )


def _format_signal(signal: dict) -> str:
    """Format a single signal for display.

    Args:
        signal: Signal data

    Returns:
        Formatted signal string
    """
    direction_emoji = "🟢" if signal["direction"] == "long" else "🔴"
    direction_text = "Long" if signal["direction"] == "long" else "Short"
    strength_squares = "🟩" * signal["strength"] + "⬜" * (5 - signal["strength"])

    lines = [
        f"{direction_emoji} <b>{signal['symbol']}</b> | {signal['timeframe']}",
        f"{strength_squares} {direction_text}",
        f"⭐ Качество: {signal['quality_total']}/10",
    ]

    if signal.get("max_drawdown"):
        lines.append(f"📉 Просадка: {signal['max_drawdown']}%")

    return "\n".join(lines)


async def _show_signals(message: Message, direction: str | None = None) -> None:
    """Show signals with optional direction filter.

    Args:
        message: Incoming message
        direction: Filter by direction (long, short, None for all)
    """
    try:
        data = await bablo_client.get_signals(limit=10, direction=direction)
        signals = data.get("items", [])

        if not signals:
            filter_text = ""
            if direction == "long":
                filter_text = " Long"
            elif direction == "short":
                filter_text = " Short"

            await message.answer(
                f"📋 <b>Сигналы{filter_text}</b>\n\n"
                "Сигналов пока нет."
            )
            return

        header = "📋 <b>Последние сигналы"
        if direction == "long":
            header = "🟢 <b>Long сигналы"
        elif direction == "short":
            header = "🔴 <b>Short сигналы"
        header += "</b>\n"

        formatted_signals = [_format_signal(s) for s in signals]
        text = header + "\n" + "\n\n".join(formatted_signals)

        total = data.get("total", len(signals))
        if total > len(signals):
            text += f"\n\n<i>Показано {len(signals)} из {total}</i>"

        await message.answer(text)

    except Exception as e:
        await message.answer(
            f"❌ <b>Ошибка</b>\n\n"
            f"Не удалось получить сигналы: {str(e)}\n\n"
            "Попробуйте позже."
        )


@router.message(F.text == "🟢 Long сигналы")
async def bablo_long_signals(message: Message) -> None:
    """Show Long signals."""
    await _show_signals(message, "long")


@router.message(F.text == "🔴 Short сигналы")
async def bablo_short_signals(message: Message) -> None:
    """Show Short signals."""
    await _show_signals(message, "short")


@router.message(F.text == "📋 Все сигналы")
async def bablo_all_signals(message: Message) -> None:
    """Show all signals."""
    await _show_signals(message, None)

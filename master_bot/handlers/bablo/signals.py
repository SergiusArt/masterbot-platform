"""Bablo signals handlers."""

from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.bablo_menu import get_bablo_signals_keyboard
from services.bablo_client import bablo_client
from shared.constants import MENU_BABLO_SIGNALS
from states.navigation import MenuState

router = Router()


@router.message(F.text == MENU_BABLO_SIGNALS)
async def bablo_signals_menu(message: Message, state: FSMContext) -> None:
    """Handle Bablo signals menu.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_signals)
    await message.answer(
        "📋 <b>Сигналы Bablo</b>\n\n"
        "Выберите тип сигналов или таймфрейм:",
        reply_markup=get_bablo_signals_keyboard(),
    )


def _format_time(received_at: str) -> str:
    """Format received_at time in short format.

    Args:
        received_at: ISO format datetime string

    Returns:
        Short time format like "14:35" or "Вчера 14:35"
    """
    try:
        dt = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)

        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        elif (now.date() - dt.date()).days == 1:
            return f"Вчера {dt.strftime('%H:%M')}"
        else:
            return dt.strftime("%d.%m %H:%M")
    except Exception:
        return ""


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

    time_str = _format_time(signal.get("received_at", ""))
    time_part = f" | {time_str}" if time_str else ""

    lines = [
        f"{direction_emoji} <b>{signal['symbol']}</b> | {signal['timeframe']}{time_part}",
        f"{strength_squares} {direction_text}",
        f"⭐ Качество: {signal['quality_total']}/10",
    ]

    if signal.get("max_drawdown"):
        lines.append(f"📉 Просадка: {signal['max_drawdown']}%")

    return "\n".join(lines)


async def _show_signals(
    message: Message,
    direction: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> None:
    """Show signals with optional direction and timeframe filters.

    Args:
        message: Incoming message
        direction: Filter by direction (long, short, None for all)
        timeframe: Filter by timeframe (15m, 1h, 4h, None for all)
    """
    try:
        data = await bablo_client.get_signals(
            limit=10, direction=direction, timeframe=timeframe
        )
        signals = data.get("signals", [])

        if not signals:
            filter_parts = []
            if direction == "long":
                filter_parts.append("Long")
            elif direction == "short":
                filter_parts.append("Short")
            if timeframe:
                filter_parts.append(timeframe)

            filter_text = " " + " ".join(filter_parts) if filter_parts else ""

            await message.answer(
                f"📋 <b>Сигналы{filter_text}</b>\n\n"
                "Сигналов пока нет."
            )
            return

        header_parts = ["📋 <b>"]
        if direction == "long":
            header_parts = ["🟢 <b>Long"]
        elif direction == "short":
            header_parts = ["🔴 <b>Short"]
        else:
            header_parts = ["📋 <b>Последние"]

        header_parts.append(" сигналы")
        if timeframe:
            header_parts.append(f" ({timeframe})")
        header_parts.append("</b>\n")
        header = "".join(header_parts)

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
    await _show_signals(message, direction="long")


@router.message(F.text == "🔴 Short сигналы")
async def bablo_short_signals(message: Message) -> None:
    """Show Short signals."""
    await _show_signals(message, direction="short")


@router.message(F.text == "📋 Все сигналы")
async def bablo_all_signals(message: Message) -> None:
    """Show all signals."""
    await _show_signals(message)


@router.message(F.text == "⏱ 15м")
async def bablo_signals_15m(message: Message) -> None:
    """Show signals with 15m timeframe."""
    await _show_signals(message, timeframe="15m")


@router.message(F.text == "⏱ 1ч")
async def bablo_signals_1h(message: Message) -> None:
    """Show signals with 1h timeframe."""
    await _show_signals(message, timeframe="1h")


@router.message(F.text == "⏱ 4ч")
async def bablo_signals_4h(message: Message) -> None:
    """Show signals with 4h timeframe."""
    await _show_signals(message, timeframe="4h")

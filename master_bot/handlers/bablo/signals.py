"""Bablo signals handlers."""

import re
from datetime import datetime
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.bablo_menu import (
    get_bablo_signals_keyboard,
    get_bablo_menu_keyboard,
    get_timeframe_selection_keyboard,
)
from services.bablo_client import bablo_client
from shared.constants import MENU_BABLO_SIGNALS, MENU_BACK, MENU_MAIN
from states.navigation import MenuState

router = Router()

# Timeframe to strength mapping
TIMEFRAME_STRENGTH = {
    "1м": 1,
    "5м": 2,
    "15м": 3,
    "30м": 4,
    "1ч": 5,
}

# Strength to timeframe mapping
STRENGTH_TIMEFRAME = {v: k for k, v in TIMEFRAME_STRENGTH.items()}


@router.message(F.text == MENU_BABLO_SIGNALS)
async def bablo_signals_menu(message: Message, state: FSMContext) -> None:
    """Handle Bablo signals menu - direction selection.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_signals)
    await state.update_data(selected_timeframes=set(), signal_direction=None)
    await message.answer(
        "📋 <b>Сигналы Bablo</b>\n\n"
        "Здесь отображаются <b>все сигналы за текущий день</b>, которые соответствуют вашим фильтрам.\n\n"
        "Выберите направление сигналов для просмотра:",
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
    strength = signal.get("strength", 1)
    strength_squares = "🟩" * strength + "⬜" * (5 - strength)

    # Get timeframe from strength
    timeframe = STRENGTH_TIMEFRAME.get(strength, signal.get("timeframe", ""))

    time_str = _format_time(signal.get("received_at", ""))
    time_part = f" | {time_str}" if time_str else ""

    lines = [
        f"{direction_emoji} <b>{signal['symbol']}</b> | {timeframe}{time_part}",
        f"{strength_squares} {direction_text}",
        f"⭐ Качество: {signal['quality_total']}/10",
    ]

    if signal.get("max_drawdown"):
        lines.append(f"📉 Просадка: {signal['max_drawdown']}%")

    return "\n".join(lines)


async def _show_signals(
    message: Message,
    direction: Optional[str] = None,
    timeframes: Optional[set[str]] = None,
) -> None:
    """Show signals with optional direction and timeframe filters.

    Args:
        message: Incoming message
        direction: Filter by direction (long, short, None for all)
        timeframes: Set of timeframes to filter by (e.g., {"1м", "5м"})
    """
    try:
        # Convert timeframes to strengths for API query
        strengths = None
        if timeframes:
            strengths = [TIMEFRAME_STRENGTH[tf] for tf in timeframes if tf in TIMEFRAME_STRENGTH]

        data = await bablo_client.get_signals(
            limit=10,
            direction=direction,
            min_strength=min(strengths) if strengths else None,
            max_strength=max(strengths) if strengths else None,
        )
        signals = data.get("signals", [])

        # Filter by exact strengths if specified
        if strengths:
            signals = [s for s in signals if s.get("strength") in strengths]

        if not signals:
            filter_parts = []
            if direction == "long":
                filter_parts.append("Long")
            elif direction == "short":
                filter_parts.append("Short")
            if timeframes:
                filter_parts.append(f"({', '.join(sorted(timeframes))})")

            filter_text = " " + " ".join(filter_parts) if filter_parts else ""

            await message.answer(
                f"📋 <b>Сигналы{filter_text}</b>\n\n"
                "Сигналов пока нет."
            )
            return

        header_parts = []
        if direction == "long":
            header_parts.append("🟢 <b>Long сигналы")
        elif direction == "short":
            header_parts.append("🔴 <b>Short сигналы")
        else:
            header_parts.append("📋 <b>Все сигналы")

        if timeframes:
            header_parts.append(f" ({', '.join(sorted(timeframes))})")
        header_parts.append("</b>\n")
        header = "".join(header_parts)

        formatted_signals = [_format_signal(s) for s in signals[:10]]
        text = header + "\n" + "\n\n".join(formatted_signals)

        total = data.get("total", len(signals))
        if total > len(formatted_signals):
            text += f"\n\n<i>Показано {len(formatted_signals)} из {total}</i>"

        await message.answer(text)

    except Exception as e:
        await message.answer(
            f"❌ <b>Ошибка</b>\n\n"
            f"Не удалось получить сигналы: {str(e)}\n\n"
            "Попробуйте позже."
        )


async def _go_to_timeframe_selection(message: Message, state: FSMContext, direction: Optional[str]) -> None:
    """Navigate to timeframe selection.

    Args:
        message: Incoming message
        state: FSM context
        direction: Selected direction
    """
    await state.set_state(MenuState.bablo_signals_timeframe)
    await state.update_data(signal_direction=direction, selected_timeframes=set())

    direction_text = ""
    if direction == "long":
        direction_text = " Long"
    elif direction == "short":
        direction_text = " Short"

    await message.answer(
        f"📋 <b>{direction_text} сигналы</b>\n\n"
        "Выберите таймфреймы (можно несколько).\n\n"
        "Затем нажмите «Показать сигналы»",
        reply_markup=get_timeframe_selection_keyboard(),
    )


@router.message(F.text == "🟢 Long сигналы")
async def bablo_long_signals(message: Message, state: FSMContext) -> None:
    """Select Long signals direction."""
    await _go_to_timeframe_selection(message, state, "long")


@router.message(F.text == "🔴 Short сигналы")
async def bablo_short_signals(message: Message, state: FSMContext) -> None:
    """Select Short signals direction."""
    await _go_to_timeframe_selection(message, state, "short")


@router.message(F.text == "📋 Все сигналы")
async def bablo_all_signals(message: Message, state: FSMContext) -> None:
    """Select all signals."""
    await _go_to_timeframe_selection(message, state, None)


# Timeframe toggle handlers
@router.message(MenuState.bablo_signals_timeframe, F.text.regexp(r"^[✅⬜] \d+[мч]$"))
async def toggle_timeframe(message: Message, state: FSMContext) -> None:
    """Toggle timeframe selection.

    Args:
        message: Incoming message
        state: FSM context
    """
    # Extract timeframe from button text
    match = re.search(r"(\d+[мч])$", message.text)
    if not match:
        return

    timeframe = match.group(1)
    data = await state.get_data()
    selected = data.get("selected_timeframes", set())

    if isinstance(selected, list):
        selected = set(selected)

    if timeframe in selected:
        selected.discard(timeframe)
        status_text = f"❌ {timeframe} таймфрейм снят"
    else:
        selected.add(timeframe)
        status_text = f"✅ {timeframe} таймфрейм выбран"

    await state.update_data(selected_timeframes=selected)
    await message.answer(
        status_text,
        reply_markup=get_timeframe_selection_keyboard(selected),
    )


@router.message(MenuState.bablo_signals_timeframe, F.text == "📋 Показать сигналы")
async def show_filtered_signals(message: Message, state: FSMContext) -> None:
    """Show signals with selected filters.

    Args:
        message: Incoming message
        state: FSM context
    """
    data = await state.get_data()
    direction = data.get("signal_direction")
    timeframes = data.get("selected_timeframes", set())

    if isinstance(timeframes, list):
        timeframes = set(timeframes)

    # If no timeframes selected, show all
    if not timeframes:
        timeframes = None

    await _show_signals(message, direction=direction, timeframes=timeframes)


@router.message(MenuState.bablo_signals_timeframe, F.text == MENU_BACK)
async def back_from_timeframe_selection(message: Message, state: FSMContext) -> None:
    """Go back to direction selection.

    Args:
        message: Incoming message
        state: FSM context
    """
    await state.set_state(MenuState.bablo_signals)
    await message.answer(
        "📋 <b>Сигналы Bablo</b>\n\n"
        "Выберите тип сигналов:",
        reply_markup=get_bablo_signals_keyboard(),
    )

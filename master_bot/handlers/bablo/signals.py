"""Bablo signals handlers."""

import re
from datetime import datetime, timezone
from typing import Optional

import pytz
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import settings
from keyboards.reply.bablo_menu import (
    get_bablo_signals_keyboard,
    get_bablo_menu_keyboard,
    get_timeframe_selection_keyboard,
)
from keyboards.inline.bablo import get_signals_pagination_keyboard
from services.bablo_client import bablo_client
from services.impulse_client import impulse_client
from shared.constants import MENU_BABLO_SIGNALS, MENU_BACK, MENU_MAIN
from shared.utils.timezone import get_pytz_timezone
from states.navigation import MenuState

router = Router()

SIGNALS_PER_PAGE = 10

# Button label to DB timeframe value
TIMEFRAME_TO_DB = {
    "1м": "1m",
    "5м": "5m",
    "15м": "15m",
    "30м": "30m",
    "1ч": "1h",
}

# DB timeframe value to button label
DB_TO_TIMEFRAME = {v: k for k, v in TIMEFRAME_TO_DB.items()}

# Default timezone (fallback)
_default_tz = pytz.timezone(settings.TIMEZONE)


@router.message(MenuState.bablo, F.text == MENU_BABLO_SIGNALS)
async def bablo_signals_menu(message: Message, state: FSMContext) -> None:
    """Handle Bablo signals menu - direction selection.

    Args:
        message: Incoming message
        state: FSM context
    """
    # Get user timezone
    user_id = message.from_user.id
    try:
        user_settings = await impulse_client.get_user_settings(user_id)
        user_tz = user_settings.get("timezone", "Europe/Moscow")
    except Exception:
        user_tz = "Europe/Moscow"

    await state.set_state(MenuState.bablo_signals)
    await state.update_data(selected_timeframes=set(), signal_direction=None, user_timezone=user_tz)
    await message.answer(
        "📋 <b>Сигналы Bablo</b>\n\n"
        "Здесь отображаются <b>все сигналы за текущий день</b>, которые соответствуют вашим фильтрам.\n\n"
        "Выберите направление сигналов для просмотра:",
        reply_markup=get_bablo_signals_keyboard(),
    )


def _format_time(received_at: str, user_tz_str: str | None = None) -> str:
    """Format received_at time in user's timezone.

    Args:
        received_at: ISO format datetime string (UTC)
        user_tz_str: User timezone string (e.g., "Europe/Moscow" or "UTC+3")

    Returns:
        Short time format like "14:35" or "Вчера 14:35" in user's tz
    """
    try:
        dt = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        # Get user timezone or use default
        tz = get_pytz_timezone(user_tz_str) if user_tz_str else _default_tz
        # Convert to user timezone
        dt_local = dt.astimezone(tz)
        now_local = datetime.now(tz)

        if dt_local.date() == now_local.date():
            return dt_local.strftime("%H:%M")
        elif (now_local.date() - dt_local.date()).days == 1:
            return f"Вчера {dt_local.strftime('%H:%M')}"
        else:
            return dt_local.strftime("%d.%m %H:%M")
    except Exception:
        return ""


def _format_signal(signal: dict, user_tz: str | None = None) -> str:
    """Format a single signal for display.

    Args:
        signal: Signal data
        user_tz: User timezone string

    Returns:
        Formatted signal string
    """
    is_long = signal["direction"] == "long"
    direction_emoji = "🟢" if is_long else "🔴"
    direction_text = "Long" if is_long else "Short"
    strength = signal.get("strength", 1)
    filled = "🟩" if is_long else "🟥"
    strength_squares = filled * strength + "⬜" * (5 - strength)

    # Get display timeframe from DB value
    db_timeframe = signal.get("timeframe", "")
    timeframe = DB_TO_TIMEFRAME.get(db_timeframe, db_timeframe)

    time_str = _format_time(signal.get("received_at", ""), user_tz)
    time_part = f" | {time_str}" if time_str else ""

    lines = [
        f"{direction_emoji} <b>{signal['symbol']}</b> | {timeframe}{time_part}",
        f"{strength_squares} {direction_text}",
        f"⭐ Качество: {signal['quality_total']}/10",
    ]

    if signal.get("max_drawdown"):
        lines.append(f"📉 Просадка: {signal['max_drawdown']}%")

    return "\n".join(lines)


def _build_header(
    direction: Optional[str],
    timeframes: Optional[set[str]],
) -> str:
    """Build signals list header text."""
    if direction == "long":
        header = "🟢 <b>Long сигналы"
    elif direction == "short":
        header = "🔴 <b>Short сигналы"
    else:
        header = "📋 <b>Все сигналы"

    if timeframes:
        header += f" ({', '.join(sorted(timeframes))})"
    header += "</b>\n"
    return header


async def _fetch_and_format_signals(
    direction: Optional[str],
    timeframes: Optional[set[str]],
    page: int = 0,
    user_tz: str | None = None,
) -> tuple[str, int, int]:
    """Fetch signals from API and format them.

    Returns:
        (formatted_text, total_count, shown_count)
    """
    # Convert button labels to DB timeframe values
    db_timeframes = None
    if timeframes:
        db_timeframes = [TIMEFRAME_TO_DB[tf] for tf in timeframes if tf in TIMEFRAME_TO_DB]

    data = await bablo_client.get_signals(
        limit=SIGNALS_PER_PAGE,
        offset=page * SIGNALS_PER_PAGE,
        direction=direction,
        timeframes=db_timeframes if db_timeframes else None,
    )
    signals = data.get("signals", [])
    total = data.get("total", len(signals))

    if not signals:
        return "", total, 0

    header = _build_header(direction, timeframes)
    formatted = [_format_signal(s, user_tz) for s in signals]
    text = header + "\n" + "\n\n".join(formatted)

    start_num = page * SIGNALS_PER_PAGE + 1
    end_num = start_num + len(formatted) - 1
    text += f"\n\n<i>Сигналы {start_num}–{end_num} из {total}</i>"

    return text, total, len(formatted)


async def _show_signals(
    message: Message,
    state: FSMContext,
    direction: Optional[str] = None,
    timeframes: Optional[set[str]] = None,
    page: int = 0,
) -> None:
    """Show signals with optional filters and pagination.

    Args:
        message: Incoming message
        state: FSM context
        direction: Filter by direction (long, short, None for all)
        timeframes: Set of timeframes to filter by
        page: Page number (0-based)
    """
    try:
        # Get user timezone from state
        data = await state.get_data()
        user_tz = data.get("user_timezone")

        text, total, shown = await _fetch_and_format_signals(direction, timeframes, page, user_tz)

        if not text:
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

        # Save pagination state
        await state.update_data(signals_page=page)

        # Build pagination keyboard if needed
        has_prev = page > 0
        has_next = (page + 1) * SIGNALS_PER_PAGE < total
        keyboard = get_signals_pagination_keyboard(page, has_prev, has_next) if (has_prev or has_next) else None

        await message.answer(text, reply_markup=keyboard)

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

    await _show_signals(message, state, direction=direction, timeframes=timeframes)


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


@router.callback_query(F.data.startswith("bablo:signals:page:"))
async def paginate_signals(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle pagination buttons for signals list."""
    page = int(callback.data.split(":")[-1])
    data = await state.get_data()
    direction = data.get("signal_direction")
    timeframes = data.get("selected_timeframes", set())
    user_tz = data.get("user_timezone")

    if isinstance(timeframes, list):
        timeframes = set(timeframes)
    if not timeframes:
        timeframes = None

    try:
        text, total, shown = await _fetch_and_format_signals(direction, timeframes, page, user_tz)

        if not text:
            await callback.answer("Сигналов больше нет")
            return

        await state.update_data(signals_page=page)

        has_prev = page > 0
        has_next = (page + 1) * SIGNALS_PER_PAGE < total
        keyboard = get_signals_pagination_keyboard(page, has_prev, has_next) if (has_prev or has_next) else None

        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
    except Exception:
        await callback.answer("Ошибка загрузки")

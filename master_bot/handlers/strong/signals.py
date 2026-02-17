"""Strong Signal signals handler."""

from html import escape as html_escape

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.strong_menu import get_strong_signals_keyboard
from services.strong_client import strong_client
from shared.constants import MENU_STRONG_SIGNALS, MENU_BACK, MENU_MAIN, EMOJI_HOME, animated
from states.navigation import MenuState

router = Router()


@router.message(MenuState.strong, F.text == MENU_STRONG_SIGNALS)
async def strong_signals_menu(message: Message, state: FSMContext) -> None:
    """Show Strong Signal direction selection."""
    await state.set_state(MenuState.strong_signals)
    await message.answer(
        "💪 <b>Strong Signal — Сигналы</b>\n\n"
        "Выберите направление:",
        reply_markup=get_strong_signals_keyboard(),
    )


@router.message(MenuState.strong_signals, F.text == "🧤 Long сигналы")
async def show_long_signals(message: Message, state: FSMContext) -> None:
    """Show last Long signals."""
    await _show_signals(message, direction="long")


@router.message(MenuState.strong_signals, F.text == "🎒 Short сигналы")
async def show_short_signals(message: Message, state: FSMContext) -> None:
    """Show last Short signals."""
    await _show_signals(message, direction="short")


@router.message(MenuState.strong_signals, F.text == "📋 Все сигналы")
async def show_all_signals(message: Message, state: FSMContext) -> None:
    """Show all last signals."""
    await _show_signals(message, direction=None)


async def _show_signals(message: Message, direction: str | None) -> None:
    """Fetch and display signals.

    Args:
        message: Incoming message
        direction: Direction filter or None for all
    """
    try:
        result = await strong_client.get_signals(limit=10, direction=direction)
        signals = result.get("signals", [])

        if not signals:
            dir_text = f" ({direction})" if direction else ""
            await message.answer(f"📭 Нет сигналов{dir_text}")
            return

        lines = ["💪 <b>Последние Strong Signal:</b>\n"]
        for s in signals:
            symbol = html_escape(s["symbol"])
            d = s["direction"]
            emoji = "🧤" if d == "long" else "🎒"
            dir_label = "Long" if d == "long" else "Short"
            ts = s["received_at"][:16].replace("T", " ")
            lines.append(f"{emoji} <b>{symbol}</b> — {dir_label} ({ts})")

        await message.answer("\n".join(lines))

    except Exception as e:
        await message.answer("⚠️ Не удалось загрузить сигналы. Попробуйте позже.")

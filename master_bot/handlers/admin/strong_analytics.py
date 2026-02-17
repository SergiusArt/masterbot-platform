"""Admin Strong Signal analytics handler."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply.admin_menu import get_admin_strong_keyboard, get_admin_menu_keyboard
from services.strong_client import strong_client
from shared.constants import (
    MENU_STRONG_ANALYTICS,
    MENU_BACK,
    EMOJI_CHART,
    EMOJI_CROWN,
    animated,
)
from states.navigation import MenuState

router = Router()


@router.message(MenuState.admin, F.text == MENU_STRONG_ANALYTICS)
async def strong_analytics_menu(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Show Strong Signal analytics sub-menu."""
    if not is_admin:
        return

    await state.set_state(MenuState.admin_strong)
    await message.answer(
        f"{animated(EMOJI_CHART, '📊')} <b>Strong Signal — Аналитика отработки</b>\n\n"
        "Расчёт максимального отклонения цены в сторону профита\n"
        "за 100 баров (30-мин TF) от момента сигнала.\n\n"
        "Выберите действие:",
        reply_markup=get_admin_strong_keyboard(),
    )


@router.message(MenuState.admin_strong, F.text == "📊 Статистика")
async def show_stats(message: Message, is_admin: bool = False) -> None:
    """Show performance statistics."""
    if not is_admin:
        return

    loading = await message.answer("⏳ Загружаю статистику...")

    try:
        stats = await strong_client.get_performance_stats(months=2)

        long = stats.get("by_direction", {}).get("long", {})
        short = stats.get("by_direction", {}).get("short", {})

        lines = [
            f"{animated(EMOJI_CHART, '📊')} <b>Отработка Strong Signal (2 мес.)</b>\n",
            f"📌 Всего сигналов: <b>{stats['total']}</b>",
            f"✅ Рассчитано: <b>{stats['calculated']}</b>",
            f"⏳ Ожидают: <b>{stats['pending']}</b>\n",
        ]

        if stats["calculated"] > 0:
            lines.extend([
                f"📈 Средний макс. профит: <b>{stats['avg_profit_pct']}%</b>",
                f"🟢 Лучший: <b>{stats['max_profit_pct']}%</b>",
                f"🔴 Худший: <b>{stats['min_profit_pct']}%</b>",
                f"⏱ Средн. баров до макс.: <b>{stats['avg_bars_to_max']}</b>\n",
            ])

        if long.get("count", 0) > 0:
            lines.extend([
                f"🧤 <b>Long</b> ({long['count']} шт.)",
                f"   Средний: {long['avg_profit_pct']}%  |  "
                f"Мин: {long['min_profit_pct']}%  |  Макс: {long['max_profit_pct']}%",
            ])

        if short.get("count", 0) > 0:
            lines.extend([
                f"🎒 <b>Short</b> ({short['count']} шт.)",
                f"   Средний: {short['avg_profit_pct']}%  |  "
                f"Мин: {short['min_profit_pct']}%  |  Макс: {short['max_profit_pct']}%",
            ])

        await loading.edit_text("\n".join(lines))

    except Exception as e:
        await loading.edit_text(f"❌ Ошибка: {e}")


@router.message(MenuState.admin_strong, F.text.in_({"🔄 Рассчитать", "🔄 Пересчитать всё"}))
async def calculate_performance(message: Message, is_admin: bool = False) -> None:
    """Trigger performance calculation."""
    if not is_admin:
        return

    recalculate = message.text == "🔄 Пересчитать всё"
    label = "пересчёт всех" if recalculate else "расчёт новых"
    loading = await message.answer(f"⏳ Запускаю {label} сигналов (Binance API)...")

    try:
        result = await strong_client.calculate_performance(months=2, recalculate=recalculate)

        await loading.edit_text(
            f"✅ <b>Расчёт завершён</b>\n\n"
            f"📊 Обработано: <b>{result.get('total', 0)}</b>\n"
            f"✅ Рассчитано: <b>{result.get('calculated', 0)}</b>\n"
            f"❌ Ошибок: <b>{result.get('errors', 0)}</b>"
        )

    except Exception as e:
        await loading.edit_text(f"❌ Ошибка: {e}")


@router.message(MenuState.admin_strong, F.text == "📋 Список сигналов")
async def show_signals_list(message: Message, is_admin: bool = False) -> None:
    """Show signals with performance data."""
    if not is_admin:
        return

    try:
        result = await strong_client.get_performance_signals(months=2, limit=30)
        signals = result.get("signals", [])

        if not signals:
            await message.answer("📭 Нет рассчитанных сигналов")
            return

        lines = [f"{animated(EMOJI_CHART, '📊')} <b>Сигналы с отработкой (2 мес.)</b>\n"]

        for s in signals:
            direction = s["direction"]
            emoji = "🧤" if direction == "long" else "🎒"
            dir_label = "L" if direction == "long" else "S"
            pct = s["max_profit_pct"]
            bars = s["bars_to_max"]
            ts = s["received_at"][:10]

            pct_str = f"+{pct}%" if pct >= 0 else f"{pct}%"
            lines.append(
                f"{emoji} <b>{s['symbol']}</b> {dir_label} | "
                f"{pct_str} (бар {bars}) | {ts}"
            )

        text = "\n".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "\n..."

        await message.answer(text)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(MenuState.admin_strong, F.text == MENU_BACK)
async def back_to_admin(message: Message, state: FSMContext, is_admin: bool = False) -> None:
    """Back to admin menu."""
    if not is_admin:
        return
    await state.set_state(MenuState.admin)
    await message.answer(
        f"{animated(EMOJI_CROWN, '👑')} <b>Админ-панель</b>",
        reply_markup=get_admin_menu_keyboard(),
    )

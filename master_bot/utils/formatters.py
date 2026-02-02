"""Message formatting utilities."""

from typing import Any


def format_analytics(data: dict) -> str:
    """Format analytics data for display.

    Args:
        data: Analytics data from API

    Returns:
        Formatted message string
    """
    period = data.get("period", "N/A")
    total = data.get("total_impulses", 0)
    growth = data.get("growth_count", 0)
    fall = data.get("fall_count", 0)

    period_names = {
        "today": "сегодня",
        "yesterday": "вчера",
        "week": "неделю",
        "month": "месяц",
    }
    period_name = period_names.get(period, period)

    lines = [
        f"📊 <b>Аналитика за {period_name}</b>\n",
        f"📈 Всего импульсов: <b>{total}</b>",
        f"🟢 Рост: <b>{growth}</b>",
        f"🔴 Падение: <b>{fall}</b>",
    ]

    # Top growth
    top_growth = data.get("top_growth", [])
    if top_growth:
        lines.append("\n<b>🏆 Топ рост:</b>")
        for item in top_growth[:5]:
            symbol = item.get("symbol", "N/A")
            percent = float(item.get("percent", 0))
            count = item.get("count", 1)
            lines.append(f"  • {symbol}: <b>+{percent:.1f}%</b> ({count}x)")

    # Top fall
    top_fall = data.get("top_fall", [])
    if top_fall:
        lines.append("\n<b>📉 Топ падение:</b>")
        for item in top_fall[:5]:
            symbol = item.get("symbol", "N/A")
            percent = float(item.get("percent", 0))
            count = item.get("count", 1)
            lines.append(f"  • {symbol}: <b>{percent:.1f}%</b> ({count}x)")

    # Comparison
    comparison = data.get("comparison")
    if comparison:
        vs_prev = comparison.get("vs_yesterday")
        if vs_prev is not None:
            if period == "yesterday":
                lines.append(f"\n📊 По сравнению с позавчера: <b>{vs_prev}</b>")
            else:
                lines.append(f"\n📊 По сравнению со вчера: <b>{vs_prev}</b>")

        vs_week = comparison.get("vs_week_median")
        week_median = comparison.get("week_median")
        if vs_week is not None and week_median is not None:
            lines.append(f"📈 Медиана за неделю: <b>{week_median}</b>/день ({vs_week})")

    return "\n".join(lines)


def format_impulse(data: dict) -> str:
    """Format single impulse for display.

    Args:
        data: Impulse data

    Returns:
        Formatted message string
    """
    symbol = data.get("symbol", "N/A")
    percent = float(data.get("percent", 0))
    impulse_type = data.get("type", "growth")

    if impulse_type == "growth":
        emoji = "🟢"
        direction = "Рост"
    else:
        emoji = "🔴"
        direction = "Падение"

    lines = [
        f"{emoji} <b>{symbol}</b>",
        f"Тип: {direction}",
        f"Изменение: <b>{percent:+.2f}%</b>",
    ]

    max_percent = data.get("max_percent")
    if max_percent:
        lines.append(f"Максимум: <b>{float(max_percent):+.2f}%</b>")

    return "\n".join(lines)

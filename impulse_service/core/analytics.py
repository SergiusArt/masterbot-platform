"""Core analytics calculations."""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from decimal import Decimal

from models.impulse import Impulse


def calculate_activity_level(impulses: List[Impulse]) -> str:
    """Calculate market activity level.

    Args:
        impulses: List of impulses

    Returns:
        Activity level string (low, medium, high, extreme)
    """
    count = len(impulses)

    if count < 5:
        return "low"
    elif count < 15:
        return "medium"
    elif count < 30:
        return "high"
    else:
        return "extreme"


def calculate_trend(impulses: List[Impulse]) -> str:
    """Calculate market trend based on impulses.

    Args:
        impulses: List of impulses

    Returns:
        Trend string (bullish, bearish, neutral)
    """
    if not impulses:
        return "neutral"

    growth_count = sum(1 for i in impulses if i.type == "growth")
    fall_count = len(impulses) - growth_count

    if growth_count > fall_count * 1.5:
        return "bullish"
    elif fall_count > growth_count * 1.5:
        return "bearish"
    else:
        return "neutral"


def calculate_volatility(impulses: List[Impulse]) -> str:
    """Calculate market volatility.

    Args:
        impulses: List of impulses

    Returns:
        Volatility level (low, medium, high)
    """
    if not impulses:
        return "low"

    avg_percent = sum(abs(float(i.percent)) for i in impulses) / len(impulses)

    if avg_percent < 10:
        return "low"
    elif avg_percent < 20:
        return "medium"
    else:
        return "high"


def group_by_symbol(impulses: List[Impulse]) -> Dict[str, List[Impulse]]:
    """Group impulses by symbol.

    Args:
        impulses: List of impulses

    Returns:
        Dictionary mapping symbol to impulses
    """
    result: Dict[str, List[Impulse]] = {}

    for impulse in impulses:
        if impulse.symbol not in result:
            result[impulse.symbol] = []
        result[impulse.symbol].append(impulse)

    return result


def get_most_active_symbols(
    impulses: List[Impulse],
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Get most active symbols by impulse count.

    Args:
        impulses: List of impulses
        limit: Maximum symbols to return

    Returns:
        List of symbol activity data
    """
    grouped = group_by_symbol(impulses)

    result = []
    for symbol, symbol_impulses in grouped.items():
        max_growth = max(
            (i.percent for i in symbol_impulses if i.type == "growth"),
            default=Decimal(0),
        )
        max_fall = min(
            (i.percent for i in symbol_impulses if i.type == "fall"),
            default=Decimal(0),
        )

        result.append({
            "symbol": symbol,
            "count": len(symbol_impulses),
            "max_growth": float(max_growth),
            "max_fall": float(max_fall),
        })

    # Sort by count descending
    result.sort(key=lambda x: x["count"], reverse=True)

    return result[:limit]

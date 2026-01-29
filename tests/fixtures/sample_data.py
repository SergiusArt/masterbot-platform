"""Sample test data for MasterBot Platform tests."""

from datetime import datetime, timezone
from decimal import Decimal


# ============================================================================
# Impulse Message Samples
# ============================================================================

IMPULSE_MESSAGES = {
    # Standard growth signal with all fields
    "growth_full": """🟢[SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/) **10%**
📈|29%|---|71%|📉
Максимальный импульс: 15%""",

    # Standard fall signal with all fields
    "fall_full": """🔴[AXSUSDT.P](https://ru.tradingview.com/symbols/AXSUSDT.P/) **-15%**
📈|35%|---|65%|📉
Максимальный импульс: 25%""",

    # Minimal growth signal
    "growth_minimal": """[BTCUSDT](https://example.com) **8%**""",

    # Minimal fall signal
    "fall_minimal": """[ETHUSDT](https://example.com) **-12%**""",

    # Simple format without markdown
    "simple_growth": "BTCUSDT +25.5%",
    "simple_fall": "ETHUSDT -12.3%",

    # Ratio format
    "ratio_growth": "BTC/USDT: 15.5%",
    "ratio_fall": "ETH/BTC: -8.2%",

    # Dollar format
    "dollar_growth": "$BTC +8.7%",
    "dollar_fall": "$ETH -5.5%",

    # Edge cases
    "zero_percent": "BTCUSDT 0%",
    "large_percent": "BTCUSDT +999%",
    "small_decimal": "BTCUSDT 0.1%",

    # Invalid messages (should not match)
    "invalid_no_symbol": "This has 10% but no symbol",
    "invalid_no_percent": "BTCUSDT without percent",
    "invalid_empty": "",
}


# ============================================================================
# Bablo Signal Samples
# ============================================================================

BABLO_MESSAGES = {
    # Full long signal with all fields
    "long_full": """[SYNUSDT.P](https://ru.tradingview.com/symbols/SYNUSDT.P/)
🟩🟩🟩🟩🟩
`| 1м ТФ |`
**Качество = 7 из 10:**
  ° Профитность _8_ из 10
  ° Просадка _6_ из 10
  ° Точность _7_ из 10

**Вероятность (60 минут):**
`0.3%`: 📉 `86%`, 📈 `72%`
`0.6%`: 📉 `75%`, 📈 `60%`

Максимальная просадка = __6%__""",

    # Full short signal
    "short_full": """[BTCUSDT.P](https://ru.tradingview.com/symbols/BTCUSDT.P/)
🟥🟥🟥
`| 15м ТФ |`
**Качество = 8 из 10:**
  ° Профитность _10_ из 10
  ° Просадка _4_ из 10
  ° Точность _10_ из 10

**Вероятность (12 часов):**
`0.9%`: 📉 `82%`, 📈 `73%`
`1.5%`: 📉 `75%`, 📈 `66%`
`2.7%`: 📉 `55%`, 📈 `45%`

Максимальная просадка = __17%__""",

    # Minimal signal
    "long_minimal": """[XRPUSDT.P](https://example.com)
🟩🟩
`| 1ч ТФ |`
**Качество = 5 из 10:**

**Вероятность (2 дня):**
`1.0%`: 📉 `70%`, 📈 `65%`

Максимальная просадка = __10%__""",

    # Different timeframes
    "tf_1m": """[BTCUSDT.P](https://example.com)
🟩🟩🟩
`| 1м ТФ |`
**Качество = 6 из 10:**
**Вероятность (60 минут):**
`0.5%`: 📉 `75%`, 📈 `70%`
Максимальная просадка = __5%__""",

    "tf_15m": """[ETHUSDT.P](https://example.com)
🟩🟩🟩🟩
`| 15м ТФ |`
**Качество = 7 из 10:**
**Вероятность (4 часа):**
`1.0%`: 📉 `80%`, 📈 `75%`
Максимальная просадка = __8%__""",

    "tf_1h": """[XRPUSDT.P](https://example.com)
🟩🟩
`| 1ч ТФ |`
**Качество = 5 из 10:**
**Вероятность (1 день):**
`2.0%`: 📉 `65%`, 📈 `60%`
Максимальная просадка = __15%__""",

    "tf_4h": """[SOLUSDT.P](https://example.com)
🟥🟥🟥🟥
`| 4ч ТФ |`
**Качество = 8 из 10:**
**Вероятность (3 дня):**
`3.0%`: 📉 `70%`, 📈 `65%`
Максимальная просадка = __12%__""",

    # Edge cases
    "high_quality": """[BTCUSDT.P](https://example.com)
🟩🟩🟩🟩🟩
`| 1м ТФ |`
**Качество = 10 из 10:**
  ° Профитность _10_ из 10
  ° Просадка _10_ из 10
  ° Точность _10_ из 10
**Вероятность (30 минут):**
`0.3%`: 📉 `95%`, 📈 `92%`
Максимальная просадка = __2%__""",

    "low_quality": """[BTCUSDT.P](https://example.com)
🟥
`| 4ч ТФ |`
**Качество = 1 из 10:**
  ° Профитность _1_ из 10
  ° Просадка _1_ из 10
  ° Точность _1_ из 10
**Вероятность (7 дней):**
`5.0%`: 📉 `52%`, 📈 `48%`
Максимальная просадка = __45%__""",

    # Invalid messages
    "invalid_no_direction": """[BTCUSDT.P](https://example.com)
`| 1м ТФ |`
**Качество = 5 из 10:**""",

    "invalid_no_symbol": """🟩🟩🟩
`| 1м ТФ |`
**Качество = 5 из 10:**""",

    "invalid_no_timeframe": """[BTCUSDT.P](https://example.com)
🟩🟩🟩
**Качество = 5 из 10:**""",

    "invalid_no_quality": """[BTCUSDT.P](https://example.com)
🟩🟩🟩
`| 1м ТФ |`""",

    "invalid_empty": "",
}


# ============================================================================
# Signal Data Objects
# ============================================================================

IMPULSE_DATA = {
    "growth": {
        "symbol": "BTCUSDT",
        "percent": Decimal("15.5"),
        "max_percent": Decimal("20.0"),
        "type": "growth",
        "growth_ratio": Decimal("65"),
        "fall_ratio": Decimal("35"),
        "raw_message": IMPULSE_MESSAGES["growth_full"],
    },
    "fall": {
        "symbol": "ETHUSDT",
        "percent": Decimal("-12.3"),
        "max_percent": Decimal("18.0"),
        "type": "fall",
        "growth_ratio": Decimal("40"),
        "fall_ratio": Decimal("60"),
        "raw_message": IMPULSE_MESSAGES["fall_full"],
    },
}

BABLO_SIGNAL_DATA = {
    "long": {
        "symbol": "SYNUSDT.P",
        "direction": "long",
        "strength": 5,
        "timeframe": "1m",
        "time_horizon": "60 минут",
        "quality_total": 7,
        "quality_profit": 8,
        "quality_drawdown": 6,
        "quality_accuracy": 7,
        "probabilities": {
            "0.3": {"long": 72, "short": 86},
            "0.6": {"long": 60, "short": 75},
        },
        "max_drawdown": Decimal("6"),
        "raw_message": BABLO_MESSAGES["long_full"],
    },
    "short": {
        "symbol": "BTCUSDT.P",
        "direction": "short",
        "strength": 3,
        "timeframe": "15m",
        "time_horizon": "12 часов",
        "quality_total": 8,
        "quality_profit": 10,
        "quality_drawdown": 4,
        "quality_accuracy": 10,
        "probabilities": {
            "0.9": {"long": 73, "short": 82},
            "1.5": {"long": 66, "short": 75},
            "2.7": {"long": 45, "short": 55},
        },
        "max_drawdown": Decimal("17"),
        "raw_message": BABLO_MESSAGES["short_full"],
    },
}


# ============================================================================
# User Data
# ============================================================================

USER_DATA = {
    "admin": {
        "telegram_id": 123456789,
        "username": "admin_user",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": True,
        "is_admin": True,
    },
    "regular": {
        "telegram_id": 987654321,
        "username": "regular_user",
        "first_name": "Regular",
        "last_name": "User",
        "is_active": True,
        "is_admin": False,
    },
    "inactive": {
        "telegram_id": 111222333,
        "username": "inactive_user",
        "first_name": "Inactive",
        "last_name": "User",
        "is_active": False,
        "is_admin": False,
    },
}


# ============================================================================
# Notification Settings
# ============================================================================

NOTIFICATION_SETTINGS = {
    "default": {
        "user_id": 123456789,
        "notifications_enabled": True,
        "growth_threshold": 20,
        "fall_threshold": -15,
        "morning_report": True,
        "evening_report": True,
        "weekly_report": True,
        "monthly_report": True,
        "activity_window_minutes": 15,
        "activity_threshold": 10,
    },
    "custom": {
        "user_id": 987654321,
        "notifications_enabled": True,
        "growth_threshold": 30,
        "fall_threshold": -25,
        "morning_report": False,
        "evening_report": True,
        "weekly_report": True,
        "monthly_report": False,
        "activity_window_minutes": 30,
        "activity_threshold": 15,
    },
    "disabled": {
        "user_id": 111222333,
        "notifications_enabled": False,
        "growth_threshold": 50,
        "fall_threshold": -50,
        "morning_report": False,
        "evening_report": False,
        "weekly_report": False,
        "monthly_report": False,
        "activity_window_minutes": 60,
        "activity_threshold": 100,
    },
}


# ============================================================================
# Analytics Data
# ============================================================================

ANALYTICS_DATA = {
    "today": {
        "period": "today",
        "total_impulses": 150,
        "growth_count": 90,
        "fall_count": 60,
        "top_growth": [
            {"symbol": "BTCUSDT", "percent": Decimal("25.5"), "count": 15},
            {"symbol": "ETHUSDT", "percent": Decimal("20.0"), "count": 12},
            {"symbol": "XRPUSDT", "percent": Decimal("18.5"), "count": 10},
        ],
        "top_fall": [
            {"symbol": "DOGEUSDT", "percent": Decimal("-15.5"), "count": 8},
            {"symbol": "SOLUSDT", "percent": Decimal("-12.0"), "count": 6},
        ],
    },
    "week": {
        "period": "week",
        "total_impulses": 850,
        "growth_count": 500,
        "fall_count": 350,
        "top_growth": [
            {"symbol": "BTCUSDT", "percent": Decimal("45.0"), "count": 85},
            {"symbol": "ETHUSDT", "percent": Decimal("38.5"), "count": 72},
        ],
        "top_fall": [
            {"symbol": "DOGEUSDT", "percent": Decimal("-28.0"), "count": 45},
        ],
    },
}

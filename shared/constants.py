"""Shared constants for MasterBot Platform."""

from enum import Enum


class ImpulseType(str, Enum):
    """Impulse type enumeration."""

    GROWTH = "growth"
    FALL = "fall"


class ReportType(str, Enum):
    """Report type enumeration."""

    MORNING = "morning"
    EVENING = "evening"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AnalyticsPeriod(str, Enum):
    """Analytics period enumeration."""

    TODAY = "today"
    YESTERDAY = "yesterday"
    WEEK = "week"
    MONTH = "month"


# Redis channels - Impulse
REDIS_CHANNEL_NOTIFICATIONS = "impulse:notifications"
REDIS_CHANNEL_ACTIVITY = "impulse:activity"
REDIS_CHANNEL_REPORTS = "impulse:reports"

# Redis channels - Bablo
REDIS_CHANNEL_BABLO = "bablo:notifications"

# Redis channels - Strong Signal
REDIS_CHANNEL_STRONG = "strong:notifications"

# Redis channels - System
REDIS_CHANNEL_ERRORS = "system:errors"
REDIS_CHANNEL_BROADCAST = "admin:broadcast"

# Event types
EVENT_IMPULSE_ALERT = "impulse_alert"
EVENT_ACTIVITY_ALERT = "activity_alert"
EVENT_REPORT_READY = "report_ready"
EVENT_BABLO_SIGNAL = "bablo_signal"
EVENT_BABLO_ACTIVITY = "bablo_activity"
EVENT_STRONG_SIGNAL = "strong_signal"
EVENT_SERVICE_ERROR = "service_error"
EVENT_ADMIN_BROADCAST = "admin_broadcast"

# Default values
DEFAULT_GROWTH_THRESHOLD = 20
DEFAULT_FALL_THRESHOLD = -15
DEFAULT_ACTIVITY_WINDOW_MINUTES = 15
DEFAULT_ACTIVITY_THRESHOLD = 10
DEFAULT_MORNING_REPORT_TIME = "08:00"
DEFAULT_EVENING_REPORT_TIME = "20:00"

# Animated custom emoji IDs (RestrictedEmoji pack)
EMOJI_CHART = "5431577498364158238"       # 📊
EMOJI_MONEY = "5375296873982604963"       # 💰
EMOJI_FIRE = "5420315771991497307"        # 🔥
EMOJI_CROWN = "5467406098367521267"       # 👑
EMOJI_HOME = "5465226866321268133"        # 🏠
EMOJI_CHART_UP = "5373001317042101552"    # 📈
EMOJI_CHART_DOWN = "5361748661640372834"  # 📉
EMOJI_BELL = "5242628160297641831"        # 🔔
EMOJI_PERSON = "5373012449597335010"      # 👤
EMOJI_LIGHTNING = "5431449001532594346"   # ⚡
EMOJI_TOOLBOX = "5449428597922079323"     # 🧰 (settings/services)
EMOJI_MEMO = "5334882760735598374"        # 📝 (reports/signals)
EMOJI_SEARCH = "5188217332748527444"      # 🔍
EMOJI_REFRESH = "5264727218734524899"     # 🔄
EMOJI_PLUS = "5226945370684140473"        # ➕
EMOJI_MINUS = "5229113891081956317"       # ➖
EMOJI_CALENDAR = "5431897022456145283"    # 📆
EMOJI_GLOBE = "5399898266265475100"       # 🌍
EMOJI_STAR = "5435957248314579621"        # ⭐
EMOJI_ROCKET = "5445284980978621387"      # 🚀
EMOJI_SPARKLES = "5472164874886846699"    # ✨
EMOJI_CHECK = "5427009714745517609"       # ✅
EMOJI_CROSS = "5465665476971471368"       # ❌
EMOJI_MEGAPHONE = "5469903029144657419"   # 📣
EMOJI_PARTY = "5436040291507247633"       # 🎉
EMOJI_TROPHY = "5409008750893734809"      # 🏆


def animated(emoji_id: str, fallback: str = "") -> str:
    """Format animated custom emoji for HTML messages.

    Args:
        emoji_id: Custom emoji ID from RestrictedEmoji pack
        fallback: Fallback text for clients that don't support custom emoji

    Returns:
        HTML tag for custom emoji
    """
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


# Menu button texts (no emoji prefix — animated emoji via icon_custom_emoji_id)
MENU_MAIN = "Главное меню"
MENU_BACK = "◀️ Назад"
MENU_IMPULSES = "Импульсы"
MENU_BABLO = "Bablo"
MENU_STRONG = "Strong Signal"
MENU_ANALYTICS = "Аналитика"
MENU_NOTIFICATIONS = "Уведомления"
MENU_REPORTS = "Отчёты"
MENU_ACTIVITY = "Активность"
MENU_SETTINGS = "Настройки"
MENU_ADMIN = "Админ-панель"
MENU_USERS = "Пользователи"
MENU_SERVICES = "Сервисы"

# Strong Signal menu buttons
MENU_STRONG_SIGNALS = "Сигналы"
MENU_STRONG_SETTINGS = "Настройки"

# Bablo menu buttons
MENU_BABLO_ANALYTICS = "Статистика"
MENU_BABLO_SIGNALS = "Сигналы"
MENU_BABLO_SETTINGS = "Настройки"
MENU_BABLO_TIMEFRAMES = "⏱ Таймфреймы"
MENU_BABLO_DIRECTIONS = "📈 Направления"
MENU_BABLO_QUALITY = "⭐ Качество"

# Bablo timeframes
BABLO_TIMEFRAMES = ["1m", "15m", "1h", "4h"]

# Analytics period buttons
MENU_TODAY = "За сегодня"
MENU_YESTERDAY = "За вчера"
MENU_WEEK = "За неделю"
MENU_MONTH = "За месяц"

# Report buttons
MENU_MORNING_REPORT = "🌅 Утренний"
MENU_EVENING_REPORT = "🌆 Вечерний"
MENU_WEEKLY_REPORT = "📊 Недельный"
MENU_MONTHLY_REPORT = "📊 Месячный"

# Admin buttons
MENU_ADD_USER = "Добавить"
MENU_REMOVE_USER = "Удалить"
MENU_EXTEND_ACCESS = "Продлить доступ"
MENU_USER_LIST = "Список"
MENU_SERVICE_STATUS = "Статус сервисов"
MENU_RESTART_SERVICE = "Перезапустить"
MENU_STRONG_ANALYTICS = "Strong Аналитика"

# Private chat topic sections
TOPIC_IMPULSES = "impulses"
TOPIC_BABLO = "bablo"
TOPIC_REPORTS = "reports"
TOPIC_STRONG = "strong"

# Topic display names and icon colors (Telegram color IDs)
TOPIC_CONFIG = {
    TOPIC_IMPULSES: {"name": "📊 Импульсы", "icon_color": 0x6FB9F0},
    TOPIC_BABLO: {"name": "💰 Бабло", "icon_color": 0xFFD67E},
    TOPIC_REPORTS: {"name": "📋 Отчёты", "icon_color": 0xCB86DB},
    TOPIC_STRONG: {"name": "💪 Strong Signal", "icon_color": 0x8EEE98},
}

# Redis key prefix for user topic storage
REDIS_KEY_TOPICS = "user_topics"

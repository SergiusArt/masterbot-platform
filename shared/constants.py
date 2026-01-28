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


# Redis channels
REDIS_CHANNEL_NOTIFICATIONS = "impulse:notifications"
REDIS_CHANNEL_ACTIVITY = "impulse:activity"
REDIS_CHANNEL_REPORTS = "impulse:reports"

# Event types
EVENT_IMPULSE_ALERT = "impulse_alert"
EVENT_ACTIVITY_ALERT = "activity_alert"
EVENT_REPORT_READY = "report_ready"

# Default values
DEFAULT_GROWTH_THRESHOLD = 20
DEFAULT_FALL_THRESHOLD = -15
DEFAULT_ACTIVITY_WINDOW_MINUTES = 15
DEFAULT_ACTIVITY_THRESHOLD = 10
DEFAULT_MORNING_REPORT_TIME = "08:00"
DEFAULT_EVENING_REPORT_TIME = "20:00"

# Menu button texts
MENU_MAIN = "🏠 Главное меню"
MENU_BACK = "◀️ Назад"
MENU_IMPULSES = "📊 Импульсы"
MENU_ANALYTICS = "📈 Аналитика"
MENU_NOTIFICATIONS = "🔔 Уведомления"
MENU_REPORTS = "📋 Отчёты"
MENU_ACTIVITY = "⚡ Активность"
MENU_SETTINGS = "⚙️ Настройки"
MENU_ADMIN = "👑 Админ-панель"
MENU_USERS = "👥 Пользователи"
MENU_SERVICES = "🔧 Сервисы"

# Analytics period buttons
MENU_TODAY = "📅 За сегодня"
MENU_YESTERDAY = "📅 За вчера"
MENU_WEEK = "📅 За неделю"
MENU_MONTH = "📅 За месяц"

# Report buttons
MENU_MORNING_REPORT = "🌅 Утренний"
MENU_EVENING_REPORT = "🌆 Вечерний"
MENU_WEEKLY_REPORT = "📊 Недельный"
MENU_MONTHLY_REPORT = "📊 Месячный"

# Admin buttons
MENU_ADD_USER = "➕ Добавить"
MENU_REMOVE_USER = "➖ Удалить"
MENU_EXTEND_ACCESS = "📅 Продлить доступ"
MENU_USER_LIST = "📋 Список"
MENU_SERVICE_STATUS = "📊 Статус сервисов"
MENU_RESTART_SERVICE = "🔄 Перезапустить"

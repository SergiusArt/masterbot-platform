"""Navigation states for menu tracking."""

from aiogram.fsm.state import State, StatesGroup


class MenuState(StatesGroup):
    """States for tracking current menu context."""

    # Main sections
    main = State()
    impulse = State()
    bablo = State()
    reports = State()
    settings = State()
    admin = State()

    # Impulse sub-menus
    impulse_analytics = State()
    impulse_notifications = State()
    impulse_reports = State()
    impulse_activity = State()

    # Bablo sub-menus
    bablo_analytics = State()
    bablo_signals = State()
    bablo_signals_timeframe = State()  # Timeframe selection after direction
    bablo_activity = State()
    bablo_settings = State()
    bablo_settings_timeframes = State()  # Editing timeframe filter
    bablo_settings_directions = State()  # Editing direction filter

    # Strong Signal sub-menus
    strong = State()
    strong_signals = State()
    strong_settings = State()

    # Admin sub-menus
    admin_strong = State()  # Strong Signal analytics

    # Settings sub-menus
    settings_timezone = State()  # Timezone selection
    settings_timezone_custom = State()  # Custom UTC offset input
    settings_language = State()  # Language selection

"""Navigation states for menu tracking."""

from aiogram.fsm.state import State, StatesGroup


class MenuState(StatesGroup):
    """States for tracking current menu context."""

    # Main sections
    main = State()
    impulse = State()
    bablo = State()
    settings = State()

    # Impulse sub-menus
    impulse_analytics = State()
    impulse_notifications = State()
    impulse_reports = State()
    impulse_activity = State()

    # Bablo sub-menus
    bablo_analytics = State()
    bablo_signals = State()
    bablo_settings = State()

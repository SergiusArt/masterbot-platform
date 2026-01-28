"""Admin FSM states."""

from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    """States for admin operations."""

    # User management
    waiting_for_user_id = State()
    waiting_for_access_days = State()
    confirming_action = State()

    # Broadcast
    waiting_for_broadcast_message = State()
    confirming_broadcast = State()

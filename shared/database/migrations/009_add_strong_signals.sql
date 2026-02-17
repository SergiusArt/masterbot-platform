-- Migration 009: Add Strong Signal tables
-- Strong trading signals and user notification settings

-- Strong signals table
CREATE TABLE IF NOT EXISTS strong_signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    raw_message TEXT,
    telegram_message_id BIGINT,
    received_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_strong_signals_received_at ON strong_signals (received_at);
CREATE INDEX IF NOT EXISTS idx_strong_signals_symbol ON strong_signals (symbol);
CREATE INDEX IF NOT EXISTS idx_strong_signals_direction ON strong_signals (direction);

-- Strong user settings table
CREATE TABLE IF NOT EXISTS strong_user_settings (
    user_id BIGINT PRIMARY KEY,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    long_signals BOOLEAN DEFAULT TRUE,
    short_signals BOOLEAN DEFAULT TRUE,
    timezone VARCHAR(50) DEFAULT 'Europe/Moscow',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

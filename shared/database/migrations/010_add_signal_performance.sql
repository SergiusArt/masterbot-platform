-- Migration 010: Add performance tracking columns to strong_signals
-- Tracks max profit deviation after signal entry

ALTER TABLE strong_signals ADD COLUMN IF NOT EXISTS entry_price DOUBLE PRECISION;
ALTER TABLE strong_signals ADD COLUMN IF NOT EXISTS max_profit_pct DOUBLE PRECISION;
ALTER TABLE strong_signals ADD COLUMN IF NOT EXISTS max_profit_price DOUBLE PRECISION;
ALTER TABLE strong_signals ADD COLUMN IF NOT EXISTS bars_to_max INTEGER;
ALTER TABLE strong_signals ADD COLUMN IF NOT EXISTS performance_calculated_at TIMESTAMPTZ;

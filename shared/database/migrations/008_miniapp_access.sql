-- Migration: Mini App Access Control
-- Created: 2026-02-03

-- Table for Mini App access management
CREATE TABLE IF NOT EXISTS miniapp_access (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(255),
    first_name VARCHAR(255),
    access_type VARCHAR(20) NOT NULL DEFAULT 'subscription', -- 'unlimited' or 'subscription'
    expires_at TIMESTAMP WITH TIME ZONE, -- NULL for unlimited access
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notified_2_days BOOLEAN NOT NULL DEFAULT FALSE, -- Flag: notification sent 2 days before expiry
    notified_1_day BOOLEAN NOT NULL DEFAULT FALSE,  -- Flag: notification sent 1 day before expiry
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT -- Admin who granted access
);

-- Index for quick user lookup
CREATE INDEX IF NOT EXISTS idx_miniapp_access_user_id ON miniapp_access(user_id);

-- Index for finding expiring subscriptions
CREATE INDEX IF NOT EXISTS idx_miniapp_access_expires_at ON miniapp_access(expires_at) WHERE expires_at IS NOT NULL AND is_active = TRUE;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_miniapp_access_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS trigger_miniapp_access_updated_at ON miniapp_access;
CREATE TRIGGER trigger_miniapp_access_updated_at
    BEFORE UPDATE ON miniapp_access
    FOR EACH ROW
    EXECUTE FUNCTION update_miniapp_access_updated_at();

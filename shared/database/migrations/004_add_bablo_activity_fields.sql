-- Add activity monitoring fields to bablo_user_settings table
-- This allows users to get alerts when there's high market activity (many signals in short time)

ALTER TABLE bablo_user_settings
ADD COLUMN IF NOT EXISTS activity_window_minutes INTEGER DEFAULT 15,
ADD COLUMN IF NOT EXISTS activity_threshold INTEGER DEFAULT 10,
ADD COLUMN IF NOT EXISTS last_activity_alert_at TIMESTAMP WITH TIME ZONE DEFAULT NULL;

COMMENT ON COLUMN bablo_user_settings.activity_window_minutes IS 'Time window in minutes for activity detection';
COMMENT ON COLUMN bablo_user_settings.activity_threshold IS 'Number of signals in window to trigger activity alert';
COMMENT ON COLUMN bablo_user_settings.last_activity_alert_at IS 'Timestamp of last activity alert sent to prevent spam';

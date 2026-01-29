-- Add notifications_enabled column to user_notification_settings table
-- This allows users to globally disable all notifications while keeping their settings

ALTER TABLE user_notification_settings
ADD COLUMN IF NOT EXISTS notifications_enabled BOOLEAN DEFAULT true;

COMMENT ON COLUMN user_notification_settings.notifications_enabled IS 'Global toggle for all impulse notifications';

-- Migration: Add timezone and language columns to user settings tables
-- Date: 2026-02-02
-- Description: Adds per-user timezone and language settings

-- Add timezone and language to user_notification_settings (impulse service)
ALTER TABLE user_notification_settings
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Moscow',
ADD COLUMN IF NOT EXISTS language VARCHAR(5) DEFAULT 'ru';

-- Add timezone to bablo_user_settings
ALTER TABLE bablo_user_settings
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Moscow';

-- Update existing rows to have default values if NULL
UPDATE user_notification_settings SET timezone = 'Europe/Moscow' WHERE timezone IS NULL;
UPDATE user_notification_settings SET language = 'ru' WHERE language IS NULL;
UPDATE bablo_user_settings SET timezone = 'Europe/Moscow' WHERE timezone IS NULL;

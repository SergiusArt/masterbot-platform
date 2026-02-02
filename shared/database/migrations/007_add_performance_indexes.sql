-- Migration: Add performance indexes for notification queries
-- Date: 2026-02-02
-- Description: Adds indexes to user settings tables for faster notification filtering
-- These indexes optimize queries that filter users for impulse/bablo notifications

-- Impulse service: user_notification_settings
-- Index for growth impulse notifications (WHERE growth_threshold <= X)
CREATE INDEX IF NOT EXISTS idx_user_notif_growth_threshold
ON user_notification_settings(growth_threshold);

-- Index for fall impulse notifications (WHERE fall_threshold >= X)
CREATE INDEX IF NOT EXISTS idx_user_notif_fall_threshold
ON user_notification_settings(fall_threshold);

-- Index for activity alerts (WHERE activity_threshold > 0)
CREATE INDEX IF NOT EXISTS idx_user_notif_activity_threshold
ON user_notification_settings(activity_threshold)
WHERE activity_threshold > 0;

-- Index for morning reports (WHERE morning_report = true)
CREATE INDEX IF NOT EXISTS idx_user_notif_morning_report
ON user_notification_settings(morning_report)
WHERE morning_report = true;

-- Index for evening reports (WHERE evening_report = true)
CREATE INDEX IF NOT EXISTS idx_user_notif_evening_report
ON user_notification_settings(evening_report)
WHERE evening_report = true;

-- Bablo service: bablo_user_settings
-- Composite index for signal notifications (WHERE notifications_enabled AND min_quality <= X)
CREATE INDEX IF NOT EXISTS idx_bablo_settings_notif_quality
ON bablo_user_settings(notifications_enabled, min_quality)
WHERE notifications_enabled = true;

-- Index for activity alerts (WHERE activity_threshold > 0)
CREATE INDEX IF NOT EXISTS idx_bablo_settings_activity_threshold
ON bablo_user_settings(activity_threshold)
WHERE activity_threshold > 0;

-- Index for morning reports
CREATE INDEX IF NOT EXISTS idx_bablo_settings_morning_report
ON bablo_user_settings(morning_report)
WHERE morning_report = true;

-- Index for evening reports
CREATE INDEX IF NOT EXISTS idx_bablo_settings_evening_report
ON bablo_user_settings(evening_report)
WHERE evening_report = true;

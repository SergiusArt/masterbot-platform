-- Migration: Add missing timeframe columns to bablo_user_settings
-- Date: 2026-02-02
-- Description: Adds timeframe_5m and timeframe_30m boolean columns
-- These were in the model but missing from the initial table creation

ALTER TABLE bablo_user_settings
ADD COLUMN IF NOT EXISTS timeframe_5m BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS timeframe_30m BOOLEAN DEFAULT TRUE;

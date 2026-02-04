/**
 * Admin-related TypeScript types.
 */

/** Admin user model */
export interface AdminUser {
  id: number
  username?: string
  first_name?: string
  is_active: boolean
  is_admin: boolean
  access_expires_at?: string
  created_at: string
  last_activity?: string
}

/** User statistics */
export interface UserStats {
  total_users: number
  active_users: number
  expiring_soon: number
  blocked_users: number
  admins: number
}

/** Daily activity data point */
export interface DailyActivity {
  date: string
  count: number
}

/** User activity log item */
export interface UserActivityItem {
  user_id: number
  username?: string
  first_name?: string
  action: string
  created_at: string
}

/** User frequency data */
export interface UserFrequency {
  user_id: number
  username?: string
  first_name?: string
  visit_count: number
  last_visit?: string
}

/** Activity response from API */
export interface ActivityResponse {
  daily_active_users: DailyActivity[]
  recent_logins: UserActivityItem[]
  user_frequency: UserFrequency[]
}

/** Service health status */
export interface ServiceStatus {
  name: string
  display_name: string
  status: 'healthy' | 'unhealthy'
  latency_ms?: number
  error?: string
}

/** Broadcast history item */
export interface BroadcastHistoryItem {
  id: string
  message: string
  sent_to: number
  created_at: string
  created_by?: number
}

/** Request to add user */
export interface AddUserRequest {
  user_id: number
  days: number
  username?: string
  first_name?: string
}

/** Request to update user */
export interface UpdateUserRequest {
  is_active?: boolean
  extend_days?: number
  is_admin?: boolean
}

/** Request to send broadcast */
export interface BroadcastRequest {
  message: string
  user_ids?: number[]
}

/** User info in summary response */
export interface UserInfo {
  id: number
  username?: string
  first_name?: string
  is_admin: boolean
}

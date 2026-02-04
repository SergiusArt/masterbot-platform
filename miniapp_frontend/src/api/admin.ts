/**
 * Admin API functions.
 */

import type {
  AdminUser,
  UserStats,
  ActivityResponse,
  ServiceStatus,
  BroadcastHistoryItem,
  AddUserRequest,
  UpdateUserRequest,
  BroadcastRequest,
} from '../types/admin'

const API_BASE = '/api/v1/admin'

/**
 * Get initData for authentication.
 */
function getInitData(): string {
  return window.Telegram?.WebApp?.initData || ''
}

/**
 * Make authenticated API request.
 */
async function fetchAdminApi<T>(
  endpoint: string,
  options?: {
    method?: string
    body?: unknown
  }
): Promise<T> {
  const initData = getInitData()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
  }

  const fetchOptions: RequestInit = {
    method: options?.method || 'GET',
    headers,
  }

  if (options?.body) {
    fetchOptions.body = JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE}${endpoint}`, fetchOptions)

  if (response.status === 401) {
    throw new Error('Unauthorized')
  }

  if (response.status === 403) {
    throw new Error('Admin access required')
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `API error: ${response.status}`)
  }

  return response.json()
}

export const adminApi = {
  /**
   * Get list of all users.
   */
  async getUsers(params?: {
    search?: string
    limit?: number
    offset?: number
  }): Promise<AdminUser[]> {
    const searchParams = new URLSearchParams()
    if (params?.search) searchParams.set('search', params.search)
    if (params?.limit) searchParams.set('limit', String(params.limit))
    if (params?.offset) searchParams.set('offset', String(params.offset))
    const query = searchParams.toString()
    return fetchAdminApi(`/users${query ? `?${query}` : ''}`)
  },

  /**
   * Add a new user.
   */
  async addUser(data: AddUserRequest): Promise<{
    status: string
    action: string
    user_id: number
    expires_at?: string
  }> {
    return fetchAdminApi('/users', {
      method: 'POST',
      body: data,
    })
  },

  /**
   * Update user.
   */
  async updateUser(userId: number, data: UpdateUserRequest): Promise<{
    status: string
    user_id: number
  }> {
    return fetchAdminApi(`/users/${userId}`, {
      method: 'PUT',
      body: data,
    })
  },

  /**
   * Delete (deactivate) user.
   */
  async deleteUser(userId: number): Promise<{
    status: string
    user_id: number
  }> {
    return fetchAdminApi(`/users/${userId}`, {
      method: 'DELETE',
    })
  },

  /**
   * Get user statistics.
   */
  async getStats(): Promise<UserStats> {
    return fetchAdminApi('/stats')
  },

  /**
   * Get user activity analytics.
   */
  async getActivity(days?: number): Promise<ActivityResponse> {
    const query = days ? `?days=${days}` : ''
    return fetchAdminApi(`/activity${query}`)
  },

  /**
   * Get services health.
   */
  async getServices(): Promise<ServiceStatus[]> {
    return fetchAdminApi('/services')
  },

  /**
   * Send broadcast message.
   */
  async sendBroadcast(data: BroadcastRequest): Promise<{
    status: string
    broadcast_id: string
    sent_to: number
  }> {
    return fetchAdminApi('/broadcast', {
      method: 'POST',
      body: data,
    })
  },

  /**
   * Get broadcast history.
   */
  async getBroadcastHistory(limit?: number): Promise<BroadcastHistoryItem[]> {
    const query = limit ? `?limit=${limit}` : ''
    return fetchAdminApi(`/broadcasts${query}`)
  },
}

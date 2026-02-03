import type { DashboardSummary, Impulse, BabloSignal } from '../types'

const API_BASE = '/api/v1/dashboard'

// Store initData at module level for reliable access
let storedInitData = ''

/**
 * Initialize API with Telegram initData.
 * Must be called before making any API requests.
 */
export function initApi(initData: string): void {
  storedInitData = initData
}

/**
 * Get Telegram initData for authentication.
 */
function getInitData(): string {
  // Use stored value first, fallback to window
  return storedInitData || window.Telegram?.WebApp?.initData || ''
}

/**
 * Make authenticated API request.
 */
async function fetchApi<T>(endpoint: string): Promise<T> {
  const initData = getInitData()

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  // Add auth header if we have initData
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
  }

  const response = await fetch(`${API_BASE}${endpoint}`, { headers })

  if (response.status === 401) {
    throw new Error('Unauthorized: Please open this app from Telegram')
  }

  if (response.status === 403) {
    // Parse the error detail from the response
    const errorData = await response.json().catch(() => ({}))
    const detail = errorData.detail || 'Access denied'
    const error = new Error(detail)
    ;(error as Error & { status: number }).status = 403
    throw error
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

export const api = {
  /**
   * Get combined dashboard summary.
   */
  async getSummary(): Promise<DashboardSummary> {
    return fetchApi<DashboardSummary>('/summary')
  },

  /**
   * Get impulses.
   */
  async getImpulses(params: {
    limit?: number
    offset?: number
  } = {}): Promise<{ impulses: Impulse[]; total: number }> {
    const searchParams = new URLSearchParams()
    if (params.limit) searchParams.set('limit', String(params.limit))
    if (params.offset) searchParams.set('offset', String(params.offset))
    const query = searchParams.toString()
    return fetchApi(`/impulses${query ? `?${query}` : ''}`)
  },

  /**
   * Get Bablo signals.
   */
  async getBabloSignals(params: {
    limit?: number
    offset?: number
    direction?: string
    timeframe?: string
    min_quality?: number
  } = {}): Promise<{ signals: BabloSignal[]; total: number }> {
    const searchParams = new URLSearchParams()
    if (params.limit) searchParams.set('limit', String(params.limit))
    if (params.offset) searchParams.set('offset', String(params.offset))
    if (params.direction) searchParams.set('direction', params.direction)
    if (params.timeframe) searchParams.set('timeframe', params.timeframe)
    if (params.min_quality) searchParams.set('min_quality', String(params.min_quality))
    const query = searchParams.toString()
    return fetchApi(`/bablo${query ? `?${query}` : ''}`)
  },

  /**
   * Get analytics for a service.
   */
  async getAnalytics(
    service: 'impulse' | 'bablo',
    period: 'today' | 'yesterday' | 'week' | 'month'
  ): Promise<Record<string, unknown>> {
    return fetchApi(`/analytics/${service}/${period}`)
  },

  /**
   * Check if user is authenticated (has valid initData).
   */
  isAuthenticated(): boolean {
    return !!getInitData()
  },
}

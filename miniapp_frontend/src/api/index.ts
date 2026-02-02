import type { DashboardSummary, Impulse, BabloSignal } from '../types'

const API_BASE = '/api/v1/dashboard'

async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`)
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
}

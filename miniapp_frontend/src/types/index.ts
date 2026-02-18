// Signal types
export interface Impulse {
  id: number
  symbol: string
  percent: number
  max_percent?: number
  type: 'growth' | 'fall'
  growth_ratio?: number
  fall_ratio?: number
  received_at: string
}

export interface BabloSignal {
  id: number
  symbol: string
  direction: 'long' | 'short'
  strength: number
  timeframe: string
  time_horizon?: string
  quality_total: number
  quality_profit?: number
  quality_drawdown?: number
  quality_accuracy?: number
  received_at: string
}

export interface StrongSignal {
  id: number
  symbol: string
  direction: 'long' | 'short'
  received_at: string
  entry_price: number | null
  max_profit_pct: number | null
  max_profit_price: number | null
  bars_to_max: number | null
}

export interface StrongDirectionStats {
  count: number
  avg_profit_pct: number
  min_profit_pct: number
  max_profit_pct: number
}

export interface StrongStats {
  total: number
  calculated: number
  pending: number
  avg_profit_pct: number
  min_profit_pct: number
  max_profit_pct: number
  avg_bars_to_max: number
  by_direction: {
    long: StrongDirectionStats
    short: StrongDirectionStats
  }
}

// Activity zones
export type ActivityZone = 'very_low' | 'low' | 'normal' | 'high' | 'extreme'
export type MarketPulse = 'calm' | 'normal' | 'active' | 'very_active'

// Dashboard summary
export interface ImpulseStats {
  today_count: number
  growth_count: number
  fall_count: number
  median: number
  activity_zone: ActivityZone
  activity_ratio: number
}

export interface BabloStats {
  today_count: number
  long_count: number
  short_count: number
  avg_quality: number
  median: number
  activity_zone: ActivityZone
  activity_ratio: number
}

/** User info in dashboard summary */
export interface UserInfo {
  id: number
  username?: string
  first_name?: string
  is_admin: boolean
}

export interface DashboardSummary {
  impulses: ImpulseStats
  bablo: BabloStats
  market_pulse: MarketPulse
  timestamp: string
  user: UserInfo
}

// Chart data
export interface HourlyActivity {
  hour: string
  count: number
}

export interface ActivityChartData {
  impulses: HourlyActivity[]
  bablo: HourlyActivity[]
  medians: {
    impulse_weekly: number
    bablo_weekly: number
  }
}

// Time series data
export type TimeSeriesPeriod = 'today' | 'week' | 'month'

export interface TimeSeriesData {
  period: TimeSeriesPeriod
  labels: string[]
  counts: number[]
  median: number
  total: number
}

// WebSocket messages
export type WSMessageType =
  | 'impulse:new'
  | 'impulse:stats'
  | 'bablo:new'
  | 'bablo:stats'
  | 'strong:new'
  | 'activity:zone'
  | 'connected'
  | 'error'
  | 'pong'

export interface WSMessage {
  type: WSMessageType
  data: Record<string, unknown>
  timestamp: string
}

// Tab navigation
export type TabType = 'combined' | 'impulse' | 'bablo' | 'strong' | 'reports' | 'admin'

// Reports data
export interface ServiceReport {
  period: string
  total: number
  vs_yesterday?: string
  vs_week_avg?: string
  week_median?: number
  month_median?: number
}

// Re-export admin types
export * from './admin'

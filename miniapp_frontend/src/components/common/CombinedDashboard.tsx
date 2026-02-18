import { useEffect, useState } from 'react'
import { api } from '../../api'
import type { DashboardSummary, Impulse, BabloSignal, StrongStats } from '../../types'
import { getMarketPulseLabel, getMarketPulseColor } from '../../utils/activityZone'
import { ActivityZoneBadge } from './ActivityZoneBadge'
import { LoadingSpinner } from './LoadingSpinner'
import { formatPercent, formatRelativeTime, formatQuality } from '../../utils/formatters'

interface CombinedDashboardProps {
  onNavigateToImpulse: () => void
  onNavigateToBablo: () => void
  onNavigateToStrong: () => void
}

// Combined signal type for unified feed
type CombinedSignal =
  | { type: 'impulse'; data: Impulse; timestamp: string }
  | { type: 'bablo'; data: BabloSignal; timestamp: string }

export function CombinedDashboard({ onNavigateToImpulse, onNavigateToBablo, onNavigateToStrong }: CombinedDashboardProps) {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [strongStats, setStrongStats] = useState<StrongStats | null>(null)
  const [combinedFeed, setCombinedFeed] = useState<CombinedSignal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        const [summaryData, impulsesData, babloData, strongData] = await Promise.all([
          api.getSummary(),
          api.getImpulses({ limit: 10 }),
          api.getBabloSignals({ limit: 10 }),
          api.getStrongStats().catch(() => null),
        ])

        setSummary(summaryData)
        if (strongData) setStrongStats(strongData)

        // Combine and sort by timestamp
        const impulseSignals: CombinedSignal[] = (impulsesData.impulses || []).map((i: Impulse) => ({
          type: 'impulse' as const,
          data: i,
          timestamp: i.received_at,
        }))

        const babloSignals: CombinedSignal[] = (babloData.signals || []).map((s: BabloSignal) => ({
          type: 'bablo' as const,
          data: s,
          timestamp: s.received_at,
        }))

        const combined = [...impulseSignals, ...babloSignals]
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
          .slice(0, 10)

        setCombinedFeed(combined)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()

    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (isLoading && !summary) {
    return <LoadingSpinner text="Загрузка..." />
  }

  if (error && !summary) {
    return (
      <div className="card text-center py-8">
        <span className="text-4xl">❌</span>
        <p className="mt-2 text-tg-destructive">{error}</p>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      {/* Market Pulse */}
      {summary && (
        <div className="card text-center">
          <div className="card-header">Пульс рынка</div>
          <div className={`text-3xl font-bold mt-2 ${getMarketPulseColor(summary.market_pulse)}`}>
            {getMarketPulseLabel(summary.market_pulse)}
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3">
        {/* Impulse card */}
        <button
          onClick={onNavigateToImpulse}
          className="card text-left active:opacity-80 transition-opacity"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg">⚡</span>
            {summary && <ActivityZoneBadge zone={summary.impulses.activity_zone} />}
          </div>
          <div className="stat-value">{summary?.impulses.today_count ?? '-'}</div>
          <div className="stat-label">Импульсов сегодня</div>
          <div className="mt-2 flex space-x-2 text-xs">
            <span className="text-growth">📈 {summary?.impulses.growth_count}</span>
            <span className="text-fall">📉 {summary?.impulses.fall_count}</span>
          </div>
        </button>

        {/* Bablo card */}
        <button
          onClick={onNavigateToBablo}
          className="card text-left active:opacity-80 transition-opacity"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg">💰</span>
            {summary && <ActivityZoneBadge zone={summary.bablo.activity_zone} />}
          </div>
          <div className="stat-value">{summary?.bablo.today_count ?? '-'}</div>
          <div className="stat-label">Bablo сигналов</div>
          <div className="mt-2 flex space-x-2 text-xs">
            <span className="text-long">🟢 {summary?.bablo.long_count}</span>
            <span className="text-short">🔴 {summary?.bablo.short_count}</span>
          </div>
        </button>
      </div>

      {/* Strong Signal Performance */}
      {strongStats && strongStats.calculated > 0 && (
        <button
          onClick={onNavigateToStrong}
          className="card w-full text-left active:opacity-80 transition-opacity"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-lg">🏆</span>
              <span className="card-header !mb-0">Strong Signal</span>
            </div>
            <span className="text-sm font-semibold text-tg-accent">
              {formatPercent(strongStats.avg_profit_pct)}
            </span>
          </div>
          <div className="flex justify-between text-xs text-tg-hint">
            <span>Сигналов: {strongStats.total}</span>
            <span>
              🧤 {formatPercent(strongStats.by_direction.long.avg_profit_pct)} ({strongStats.by_direction.long.count})
              {' | '}
              🎒 {formatPercent(strongStats.by_direction.short.avg_profit_pct)} ({strongStats.by_direction.short.count})
            </span>
          </div>
        </button>
      )}

      {/* Combined Feed */}
      <div className="card">
        <div className="card-header">Последняя активность</div>

        {combinedFeed.length === 0 ? (
          <div className="text-center py-6">
            <span className="text-3xl">📊</span>
            <p className="mt-2 text-tg-hint">Нет данных</p>
          </div>
        ) : (
          <div className="space-y-2 mt-2">
            {combinedFeed.map((signal, idx) => (
              <div key={`${signal.type}-${idx}`} className="flex items-center justify-between py-2 border-b border-tg-hint/10 last:border-0">
                {signal.type === 'impulse' ? (
                  <>
                    <div className="flex items-center space-x-2">
                      <span className={signal.data.type === 'growth' ? 'text-growth' : 'text-fall'}>
                        {signal.data.type === 'growth' ? '📈' : '📉'}
                      </span>
                      <span className="font-medium text-sm">{signal.data.symbol}</span>
                    </div>
                    <div className="text-right">
                      <span className={`text-sm font-semibold ${signal.data.type === 'growth' ? 'text-growth' : 'text-fall'}`}>
                        {formatPercent(signal.data.percent)}
                      </span>
                      <p className="text-xs text-tg-hint">{formatRelativeTime(signal.timestamp)}</p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex items-center space-x-2">
                      <span className={signal.data.direction === 'long' ? 'text-long' : 'text-short'}>
                        {signal.data.direction === 'long' ? '🟢' : '🔴'}
                      </span>
                      <span className="font-medium text-sm">{signal.data.symbol}</span>
                      <span className="text-xs text-tg-hint">{signal.data.timeframe}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-tg-accent">
                        Q: {formatQuality(signal.data.quality_total)}
                      </span>
                      <p className="text-xs text-tg-hint">{formatRelativeTime(signal.timestamp)}</p>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

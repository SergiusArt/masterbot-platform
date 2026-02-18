import type { StrongStats as StrongStatsType } from '../../types'
import { formatPercent } from '../../utils/formatters'

interface StrongStatsProps {
  stats: StrongStatsType
}

export function StrongStats({ stats }: StrongStatsProps) {
  return (
    <div className="card space-y-4">
      <div className="card-header">Отработка сигналов</div>

      {/* Hero: Average profit */}
      <div className="text-center py-2">
        <div className="text-xs text-tg-hint mb-1">Средний макс. профит</div>
        <div className="text-4xl font-bold text-tg-accent">
          {formatPercent(stats.avg_profit_pct)}
        </div>
        <div className="mt-1 text-xs text-tg-hint">
          Рассчитано {stats.calculated} из {stats.total} сигналов
          {stats.pending > 0 && (
            <span className="ml-1">({stats.pending} ожидают)</span>
          )}
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center">
          <div className="stat-value text-lg text-growth">
            {formatPercent(stats.max_profit_pct)}
          </div>
          <div className="stat-label">Лучший</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-lg text-tg-hint">
            {formatPercent(stats.min_profit_pct)}
          </div>
          <div className="stat-label">Худший</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-lg text-tg-text">
            {stats.avg_bars_to_max > 0 ? Math.round(stats.avg_bars_to_max) : '—'}
          </div>
          <div className="stat-label">Avg бар</div>
        </div>
      </div>

      {/* Direction breakdown */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-long/5 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <span>🧤</span>
            <span className="text-xs font-medium text-long">LONG</span>
            <span className="badge badge-long">{stats.by_direction.long.count}</span>
          </div>
          <div className="text-xl font-bold text-long">
            {formatPercent(stats.by_direction.long.avg_profit_pct)}
          </div>
          <div className="text-xs text-tg-hint mt-1">
            Лучший: {formatPercent(stats.by_direction.long.max_profit_pct)}
          </div>
        </div>

        <div className="bg-short/5 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <span>🎒</span>
            <span className="text-xs font-medium text-short">SHORT</span>
            <span className="badge badge-short">{stats.by_direction.short.count}</span>
          </div>
          <div className="text-xl font-bold text-short">
            {formatPercent(stats.by_direction.short.avg_profit_pct)}
          </div>
          <div className="text-xs text-tg-hint mt-1">
            Лучший: {formatPercent(stats.by_direction.short.max_profit_pct)}
          </div>
        </div>
      </div>
    </div>
  )
}

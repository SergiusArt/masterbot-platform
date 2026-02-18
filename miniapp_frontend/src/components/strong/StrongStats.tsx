import type { StrongStats as StrongStatsType } from '../../types'
import { formatPercent } from '../../utils/formatters'

interface StrongStatsProps {
  stats: StrongStatsType
}

export function StrongStats({ stats }: StrongStatsProps) {
  return (
    <div>
      {/* Main stats grid */}
      <div className="grid grid-cols-2 gap-3">
        {/* Average profit */}
        <div className="card">
          <div className="stat-label">Средний профит</div>
          <div className="stat-value text-tg-accent">
            {formatPercent(stats.avg_profit_pct)}
          </div>
        </div>

        {/* Best signal */}
        <div className="card">
          <div className="stat-label">Лучший сигнал</div>
          <div className="stat-value text-growth">
            {formatPercent(stats.max_profit_pct)}
          </div>
        </div>

        {/* Long stats */}
        <div className="card">
          <div className="flex items-center space-x-1 mb-1">
            <span>🧤</span>
            <span className="stat-label">Long</span>
            <span className="text-xs text-tg-hint">({stats.by_direction.long.count})</span>
          </div>
          <div className="stat-value text-long">
            {formatPercent(stats.by_direction.long.avg_profit_pct)}
          </div>
        </div>

        {/* Short stats */}
        <div className="card">
          <div className="flex items-center space-x-1 mb-1">
            <span>🎒</span>
            <span className="stat-label">Short</span>
            <span className="text-xs text-tg-hint">({stats.by_direction.short.count})</span>
          </div>
          <div className="stat-value text-short">
            {formatPercent(stats.by_direction.short.avg_profit_pct)}
          </div>
        </div>
      </div>

      {/* Summary line */}
      <div className="mt-2 text-center text-xs text-tg-hint">
        Рассчитано: {stats.calculated}/{stats.total}
        {stats.pending > 0 && <span> | Ожидают: {stats.pending}</span>}
        {stats.avg_bars_to_max > 0 && <span> | Avg бар: {Math.round(stats.avg_bars_to_max)}</span>}
      </div>
    </div>
  )
}

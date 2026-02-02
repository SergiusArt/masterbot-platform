import type { BabloStats as BabloStatsType } from '../../types'
import { ActivityZoneBadge } from '../common/ActivityZoneBadge'
import { formatQuality } from '../../utils/formatters'

interface BabloStatsProps {
  stats: BabloStatsType
}

export function BabloStats({ stats }: BabloStatsProps) {
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <span>Bablo сигналы сегодня</span>
        <ActivityZoneBadge zone={stats.activity_zone} animate />
      </div>

      <div className="grid grid-cols-4 gap-3 mt-3">
        <div className="text-center">
          <div className="stat-value text-lg">{stats.today_count}</div>
          <div className="stat-label">Всего</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-lg text-long">{stats.long_count}</div>
          <div className="stat-label">Long</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-lg text-short">{stats.short_count}</div>
          <div className="stat-label">Short</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-lg text-tg-accent">
            {formatQuality(stats.avg_quality)}
          </div>
          <div className="stat-label">Avg Q</div>
        </div>
      </div>
    </div>
  )
}

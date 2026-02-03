import type { BabloStats as BabloStatsType } from '../../types'
import { ActivityMeter } from '../common/ActivityMeter'
import { formatQuality } from '../../utils/formatters'

interface BabloStatsProps {
  stats: BabloStatsType
}

export function BabloStats({ stats }: BabloStatsProps) {
  return (
    <div className="card space-y-4">
      <div className="card-header">Bablo сигналы сегодня</div>

      <div className="grid grid-cols-4 gap-3">
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

      <ActivityMeter
        current={stats.today_count}
        median={stats.median}
        zone={stats.activity_zone}
        ratio={stats.activity_ratio}
        label="Активность"
      />
    </div>
  )
}

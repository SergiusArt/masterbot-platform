import type { ImpulseStats as ImpulseStatsType } from '../../types'
import { ActivityMeter } from '../common/ActivityMeter'

interface ImpulseStatsProps {
  stats: ImpulseStatsType
}

export function ImpulseStats({ stats }: ImpulseStatsProps) {
  return (
    <div className="card space-y-4">
      <div className="card-header">Импульсы сегодня</div>

      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="stat-value">{stats.today_count}</div>
          <div className="stat-label">Всего</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-growth">{stats.growth_count}</div>
          <div className="stat-label">📈 Рост</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-fall">{stats.fall_count}</div>
          <div className="stat-label">📉 Падение</div>
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

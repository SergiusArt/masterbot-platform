import type { ImpulseStats as ImpulseStatsType } from '../../types'
import { ActivityZoneBadge } from '../common/ActivityZoneBadge'

interface ImpulseStatsProps {
  stats: ImpulseStatsType
}

export function ImpulseStats({ stats }: ImpulseStatsProps) {
  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <span>Импульсы сегодня</span>
        <ActivityZoneBadge zone={stats.activity_zone} animate />
      </div>

      <div className="grid grid-cols-3 gap-4 mt-3">
        <div className="text-center">
          <div className="stat-value">{stats.today_count}</div>
          <div className="stat-label">Всего</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-growth">{stats.growth_count}</div>
          <div className="stat-label">Рост</div>
        </div>
        <div className="text-center">
          <div className="stat-value text-fall">{stats.fall_count}</div>
          <div className="stat-label">Падение</div>
        </div>
      </div>
    </div>
  )
}

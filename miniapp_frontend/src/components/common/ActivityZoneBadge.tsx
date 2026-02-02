import type { ActivityZone } from '../../types'
import { getActivityZoneBadgeClass, getActivityZoneLabel } from '../../utils/activityZone'

interface ActivityZoneBadgeProps {
  zone: ActivityZone
  animate?: boolean
}

export function ActivityZoneBadge({ zone, animate = false }: ActivityZoneBadgeProps) {
  return (
    <span
      className={`badge ${getActivityZoneBadgeClass(zone)} ${animate && zone === 'high' ? 'zone-pulse' : ''}`}
    >
      {getActivityZoneLabel(zone)}
    </span>
  )
}

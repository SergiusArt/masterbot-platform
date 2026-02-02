import type { ActivityZone, MarketPulse } from '../types'

/**
 * Calculate activity zone based on current count vs median.
 */
export function calculateActivityZone(current: number, median: number): ActivityZone {
  if (median === 0) return 'medium'
  const ratio = current / median
  if (ratio < 0.5) return 'low'
  if (ratio > 1.5) return 'high'
  return 'medium'
}

/**
 * Get color class for activity zone.
 */
export function getActivityZoneColor(zone: ActivityZone): string {
  switch (zone) {
    case 'low':
      return 'text-zone-low'
    case 'medium':
      return 'text-zone-medium'
    case 'high':
      return 'text-zone-high'
  }
}

/**
 * Get badge class for activity zone.
 */
export function getActivityZoneBadgeClass(zone: ActivityZone): string {
  switch (zone) {
    case 'low':
      return 'badge-zone-low'
    case 'medium':
      return 'badge-zone-medium'
    case 'high':
      return 'badge-zone-high'
  }
}

/**
 * Get label for activity zone.
 */
export function getActivityZoneLabel(zone: ActivityZone): string {
  switch (zone) {
    case 'low':
      return 'Низкая'
    case 'medium':
      return 'Средняя'
    case 'high':
      return 'Высокая'
  }
}

/**
 * Get label for market pulse.
 */
export function getMarketPulseLabel(pulse: MarketPulse): string {
  switch (pulse) {
    case 'calm':
      return 'Спокойно'
    case 'normal':
      return 'Нормально'
    case 'active':
      return 'Активно'
    case 'very_active':
      return 'Очень активно'
  }
}

/**
 * Get color for market pulse.
 */
export function getMarketPulseColor(pulse: MarketPulse): string {
  switch (pulse) {
    case 'calm':
      return 'text-zone-low'
    case 'normal':
      return 'text-zone-medium'
    case 'active':
      return 'text-zone-high'
    case 'very_active':
      return 'text-zone-high'
  }
}

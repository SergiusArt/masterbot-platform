import type { ActivityZone, MarketPulse } from '../types'

/**
 * Calculate activity zone based on current count vs median.
 */
export function calculateActivityZone(current: number, median: number): ActivityZone {
  if (median === 0) return 'normal'
  const ratio = current / median

  if (ratio < 0.25) return 'very_low'
  if (ratio < 0.75) return 'low'
  if (ratio <= 1.25) return 'normal'
  if (ratio <= 2.0) return 'high'
  return 'extreme'
}

/**
 * Get color class for activity zone.
 */
export function getActivityZoneColor(zone: ActivityZone): string {
  switch (zone) {
    case 'very_low':
      return 'text-blue-500'
    case 'low':
      return 'text-cyan-500'
    case 'normal':
      return 'text-green-500'
    case 'high':
      return 'text-orange-500'
    case 'extreme':
      return 'text-red-500'
  }
}

/**
 * Get badge class for activity zone.
 */
export function getActivityZoneBadgeClass(zone: ActivityZone): string {
  switch (zone) {
    case 'very_low':
      return 'bg-blue-500 text-white'
    case 'low':
      return 'bg-cyan-500 text-white'
    case 'normal':
      return 'bg-green-500 text-white'
    case 'high':
      return 'bg-orange-500 text-white'
    case 'extreme':
      return 'bg-red-500 text-white'
  }
}

/**
 * Get label for activity zone.
 */
export function getActivityZoneLabel(zone: ActivityZone): string {
  switch (zone) {
    case 'very_low':
      return '🥶 Очень низкая'
    case 'low':
      return '😴 Низкая'
    case 'normal':
      return '✅ Нормальная'
    case 'high':
      return '🔥 Повышенная'
    case 'extreme':
      return '🚀 Экстремальная'
  }
}

/**
 * Get label for market pulse.
 */
export function getMarketPulseLabel(pulse: MarketPulse): string {
  switch (pulse) {
    case 'calm':
      return '😴 Спокойно'
    case 'normal':
      return '✅ Нормально'
    case 'active':
      return '🔥 Активно'
    case 'very_active':
      return '🚀 Очень активно'
  }
}

/**
 * Get color for market pulse.
 */
export function getMarketPulseColor(pulse: MarketPulse): string {
  switch (pulse) {
    case 'calm':
      return 'text-blue-500'
    case 'normal':
      return 'text-green-500'
    case 'active':
      return 'text-orange-500'
    case 'very_active':
      return 'text-red-500'
  }
}

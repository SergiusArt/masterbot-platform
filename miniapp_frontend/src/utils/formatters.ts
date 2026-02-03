import { format, parseISO, formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

/**
 * Format a date string to time (HH:mm).
 */
export function formatTime(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'HH:mm')
  } catch {
    return '--:--'
  }
}

/**
 * Format a date string to date and time (dd.MM HH:mm).
 */
export function formatDateTime(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'dd.MM HH:mm')
  } catch {
    return '--.--.--:--'
  }
}

/**
 * Format a date string to relative time (e.g., "5 минут назад").
 */
export function formatRelativeTime(dateStr: string): string {
  try {
    return formatDistanceToNow(parseISO(dateStr), {
      addSuffix: true,
      locale: ru
    })
  } catch {
    return 'недавно'
  }
}

/**
 * Format percent with sign.
 */
export function formatPercent(value: number | undefined | null): string {
  if (value == null || typeof value !== 'number') return '--'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

/**
 * Format number with thousands separator.
 */
export function formatNumber(value: number | undefined | null): string {
  if (value == null || typeof value !== 'number') return '--'
  return new Intl.NumberFormat('ru-RU').format(value)
}

/**
 * Format quality score (0-10).
 */
export function formatQuality(value: number | undefined | null): string {
  if (value == null || typeof value !== 'number') return '--'
  return value.toFixed(1)
}

/**
 * Get strength indicator (squares).
 */
export function formatStrength(strength: number): string {
  return '■'.repeat(strength) + '□'.repeat(5 - strength)
}

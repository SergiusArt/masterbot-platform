import type { ActivityZone } from '../../types'

interface ActivityMeterProps {
  current: number
  median: number
  zone: ActivityZone
  ratio: number
  label?: string
}

const zoneConfig: Record<string, { color: string; textColor: string; text: string; emoji: string }> = {
  very_low: { color: 'bg-blue-500', textColor: 'text-blue-500', text: 'Очень низкая', emoji: '🥶' },
  low: { color: 'bg-cyan-500', textColor: 'text-cyan-500', text: 'Низкая', emoji: '😴' },
  normal: { color: 'bg-green-500', textColor: 'text-green-500', text: 'Нормальная', emoji: '✅' },
  medium: { color: 'bg-green-500', textColor: 'text-green-500', text: 'Нормальная', emoji: '✅' }, // alias for backwards compatibility
  high: { color: 'bg-orange-500', textColor: 'text-orange-500', text: 'Повышенная', emoji: '🔥' },
  extreme: { color: 'bg-red-500', textColor: 'text-red-500', text: 'Экстремальная', emoji: '🚀' },
}

const defaultConfig = { color: 'bg-green-500', textColor: 'text-green-500', text: 'Нормальная', emoji: '✅' }

export function ActivityMeter({ current, median, zone, ratio, label }: ActivityMeterProps) {
  const config = zoneConfig[zone] || defaultConfig
  const safeMedian = median || 50
  const safeRatio = ratio || (safeMedian > 0 ? current / safeMedian : 1)

  // Calculate position on the meter (0-100%)
  // Map ratio to position: 0 -> 0%, 0.5 -> 25%, 1.0 -> 50%, 1.5 -> 75%, 2.0+ -> 100%
  const position = Math.min(100, Math.max(0, safeRatio * 50))

  // Format ratio as percentage
  const ratioPercent = Math.round(safeRatio * 100)

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-tg-hint">{label}</span>
          <span className="text-xs font-medium">
            {config.emoji} {config.text}
          </span>
        </div>
      )}

      {/* Activity meter bar */}
      <div className="relative h-6 rounded-lg overflow-hidden bg-gradient-to-r from-blue-500 via-green-500 to-red-500">
        {/* Zone markers */}
        <div className="absolute inset-0 flex">
          <div className="w-[12.5%] border-r border-white/30" title="Очень низкая" />
          <div className="w-[25%] border-r border-white/30" title="Низкая" />
          <div className="w-[25%] border-r border-white/30" title="Нормальная" />
          <div className="w-[25%] border-r border-white/30" title="Повышенная" />
          <div className="w-[12.5%]" title="Экстремальная" />
        </div>

        {/* Median marker (always at 50%) */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg"
          style={{ left: '50%' }}
          title={`Медиана: ${safeMedian}`}
        />

        {/* Current position indicator */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-white rounded shadow-lg transition-all duration-300"
          style={{
            left: `${position}%`,
            transform: 'translateX(-50%)',
            boxShadow: '0 0 8px rgba(0,0,0,0.5)',
          }}
        />
      </div>

      {/* Stats row */}
      <div className="flex justify-between text-xs">
        <span className="text-tg-hint">
          Сегодня: <span className="font-semibold text-tg-text">{current}</span>
        </span>
        <span className="text-tg-hint">
          Медиана: <span className="font-semibold text-tg-text">{Math.round(safeMedian)}</span>
        </span>
        <span className="text-tg-hint">
          от нормы: <span className={`font-semibold ${config.textColor}`}>{ratioPercent}%</span>
        </span>
      </div>
    </div>
  )
}

// Compact version for cards
export function ActivityBadge({ zone }: { zone: ActivityZone }) {
  const config = zoneConfig[zone] || defaultConfig

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium text-white ${config.color}`}
    >
      {config.emoji} {config.text}
    </span>
  )
}

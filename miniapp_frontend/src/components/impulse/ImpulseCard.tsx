import type { Impulse } from '../../types'
import { formatPercent, formatRelativeTime } from '../../utils/formatters'

interface ImpulseCardProps {
  impulse: Impulse
}

export function ImpulseCard({ impulse }: ImpulseCardProps) {
  const isGrowth = impulse.type === 'growth'

  return (
    <div className="card flex items-center justify-between py-3">
      <div className="flex items-center space-x-3">
        <span className={`text-xl ${isGrowth ? 'text-growth' : 'text-fall'}`}>
          {isGrowth ? '📈' : '📉'}
        </span>
        <div>
          <span className="font-semibold text-tg-text">{impulse.symbol}</span>
          <p className="text-xs text-tg-hint">{formatRelativeTime(impulse.received_at)}</p>
        </div>
      </div>
      <div className="text-right">
        <span className={`font-bold ${isGrowth ? 'text-growth' : 'text-fall'}`}>
          {formatPercent(impulse.percent)}
        </span>
        {impulse.max_percent && impulse.max_percent !== impulse.percent && (
          <p className="text-xs text-tg-hint">
            макс: {formatPercent(impulse.max_percent)}
          </p>
        )}
      </div>
    </div>
  )
}

import type { BabloSignal } from '../../types'
import { formatRelativeTime, formatQuality, formatStrength } from '../../utils/formatters'

interface BabloCardProps {
  signal: BabloSignal
}

export function BabloCard({ signal }: BabloCardProps) {
  const isLong = signal.direction === 'long'

  return (
    <div className="card py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className={`text-xl ${isLong ? 'text-long' : 'text-short'}`}>
            {isLong ? '🟢' : '🔴'}
          </span>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-tg-text">{signal.symbol}</span>
              <span className={`badge ${isLong ? 'badge-long' : 'badge-short'}`}>
                {isLong ? 'LONG' : 'SHORT'}
              </span>
            </div>
            <p className="text-xs text-tg-hint">{formatRelativeTime(signal.received_at)}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-tg-hint">{signal.timeframe}</span>
            <span className="font-mono text-xs text-tg-accent">
              {formatStrength(signal.strength)}
            </span>
          </div>
          <span className="text-sm font-semibold text-tg-text">
            Q: {formatQuality(signal.quality_total)}
          </span>
        </div>
      </div>

      {signal.time_horizon && (
        <div className="mt-2 text-xs text-tg-hint">
          Горизонт: {signal.time_horizon}
        </div>
      )}
    </div>
  )
}

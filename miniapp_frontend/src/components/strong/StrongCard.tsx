import type { StrongSignal } from '../../types'
import { formatPercent, formatDateTime, formatNumber } from '../../utils/formatters'

interface StrongCardProps {
  signal: StrongSignal
}

export function StrongCard({ signal }: StrongCardProps) {
  const dirEmoji = signal.direction === 'long' ? '🧤' : '🎒'
  const dirLabel = signal.direction === 'long' ? 'Long' : 'Short'
  const dirColor = signal.direction === 'long' ? 'text-long' : 'text-short'
  const hasPerfData = signal.max_profit_pct != null

  return (
    <div className="py-2.5 border-b border-tg-hint/10 last:border-0">
      <div className="flex items-center justify-between">
        {/* Left: emoji + symbol */}
        <div className="flex items-center space-x-2">
          <span>{dirEmoji}</span>
          <span className="font-medium text-sm">{signal.symbol}</span>
          <span className={`text-xs ${dirColor}`}>{dirLabel}</span>
        </div>

        {/* Right: profit % */}
        <div className="text-right">
          {hasPerfData ? (
            <span className="text-sm font-semibold text-growth">
              {formatPercent(signal.max_profit_pct)}
            </span>
          ) : (
            <span className="text-xs text-tg-hint">Ожидает</span>
          )}
        </div>
      </div>

      {/* Second row: date + bars + entry price */}
      <div className="flex items-center justify-between mt-1">
        <span className="text-xs text-tg-hint">
          {formatDateTime(signal.received_at)}
        </span>
        <div className="flex items-center space-x-3 text-xs text-tg-hint">
          {hasPerfData && signal.bars_to_max != null && (
            <span>Бар {signal.bars_to_max}/100</span>
          )}
          {signal.entry_price != null && (
            <span>${formatNumber(signal.entry_price)}</span>
          )}
        </div>
      </div>
    </div>
  )
}

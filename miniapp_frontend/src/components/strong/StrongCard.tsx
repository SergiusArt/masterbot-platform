import type { StrongSignal } from '../../types'
import { formatPercent, formatDateTime, formatNumber } from '../../utils/formatters'

interface StrongCardProps {
  signal: StrongSignal
}

export function StrongCard({ signal }: StrongCardProps) {
  const isLong = signal.direction === 'long'
  const hasPerfData = signal.max_profit_pct != null

  return (
    <div className="card py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className={`text-xl ${isLong ? 'text-long' : 'text-short'}`}>
            {isLong ? '🧤' : '🎒'}
          </span>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-tg-text">{signal.symbol}</span>
              <span className={`badge ${isLong ? 'badge-long' : 'badge-short'}`}>
                {isLong ? 'LONG' : 'SHORT'}
              </span>
            </div>
            <p className="text-xs text-tg-hint">{formatDateTime(signal.received_at)}</p>
          </div>
        </div>
        <div className="text-right">
          {hasPerfData ? (
            <>
              <div className="text-sm font-bold text-growth">
                {formatPercent(signal.max_profit_pct)}
              </div>
              {signal.bars_to_max != null && (
                <div className="text-xs text-tg-hint">
                  бар {signal.bars_to_max}/100
                </div>
              )}
            </>
          ) : (
            <span className="badge bg-tg-secondary-bg text-tg-hint">Ожидает</span>
          )}
        </div>
      </div>

      {/* Entry price row */}
      {hasPerfData && signal.entry_price != null && (
        <div className="mt-2 flex items-center justify-between text-xs text-tg-hint border-t border-tg-hint/10 pt-2">
          <span>Вход: ${formatNumber(signal.entry_price)}</span>
          {signal.max_profit_price != null && (
            <span>Макс: ${formatNumber(signal.max_profit_price)}</span>
          )}
        </div>
      )}
    </div>
  )
}

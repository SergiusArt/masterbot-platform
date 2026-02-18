import type { StrongSignal } from '../../types'
import { StrongCard } from './StrongCard'

interface StrongSignalListProps {
  signals: StrongSignal[]
}

export function StrongSignalList({ signals }: StrongSignalListProps) {
  if (signals.length === 0) {
    return (
      <div className="card text-center py-6">
        <span className="text-3xl">🏆</span>
        <p className="mt-2 text-tg-hint">Нет сигналов за этот период</p>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">Сигналы ({signals.length})</div>
      <div className="mt-2">
        {signals.map((signal) => (
          <StrongCard key={signal.id} signal={signal} />
        ))}
      </div>
    </div>
  )
}

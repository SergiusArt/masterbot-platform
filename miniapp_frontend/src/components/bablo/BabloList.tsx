import type { BabloSignal } from '../../types'
import { BabloCard } from './BabloCard'

interface BabloListProps {
  signals: BabloSignal[]
  maxItems?: number
}

export function BabloList({ signals, maxItems = 20 }: BabloListProps) {
  const displayedSignals = signals.slice(0, maxItems)

  if (displayedSignals.length === 0) {
    return (
      <div className="card text-center py-8">
        <span className="text-4xl">💰</span>
        <p className="mt-2 text-tg-hint">Нет сигналов</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {displayedSignals.map((signal) => (
        <BabloCard key={signal.id} signal={signal} />
      ))}
    </div>
  )
}

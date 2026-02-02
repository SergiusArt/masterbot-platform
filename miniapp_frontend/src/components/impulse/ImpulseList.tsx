import type { Impulse } from '../../types'
import { ImpulseCard } from './ImpulseCard'

interface ImpulseListProps {
  impulses: Impulse[]
  maxItems?: number
}

export function ImpulseList({ impulses, maxItems = 20 }: ImpulseListProps) {
  const displayedImpulses = impulses.slice(0, maxItems)

  if (displayedImpulses.length === 0) {
    return (
      <div className="card text-center py-8">
        <span className="text-4xl">⚡</span>
        <p className="mt-2 text-tg-hint">Нет импульсов</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {displayedImpulses.map((impulse) => (
        <ImpulseCard key={impulse.id} impulse={impulse} />
      ))}
    </div>
  )
}

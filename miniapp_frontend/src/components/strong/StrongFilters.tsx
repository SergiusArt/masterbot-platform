import type { StrongPeriod } from '../../store/strongStore'

interface StrongFiltersProps {
  filterDirection: 'all' | 'long' | 'short'
  period: StrongPeriod
  onDirectionChange: (direction: 'all' | 'long' | 'short') => void
  onPeriodChange: (period: StrongPeriod) => void
}

const directions: { value: 'all' | 'long' | 'short'; label: string }[] = [
  { value: 'all', label: 'Все' },
  { value: 'long', label: '🧤 Long' },
  { value: 'short', label: '🎒 Short' },
]

const periods: { value: StrongPeriod; label: string }[] = [
  { value: 'current_month', label: 'Текущий мес.' },
  { value: 'prev_month', label: 'Прошлый мес.' },
  { value: 'all', label: 'Всё время' },
]

export function StrongFilters({
  filterDirection,
  period,
  onDirectionChange,
  onPeriodChange,
}: StrongFiltersProps) {
  return (
    <div className="space-y-2">
      {/* Direction filter */}
      <div className="flex space-x-2">
        {directions.map((d) => (
          <button
            key={d.value}
            onClick={() => onDirectionChange(d.value)}
            className={`pill ${filterDirection === d.value ? 'pill-active' : 'pill-inactive'}`}
          >
            {d.label}
          </button>
        ))}
      </div>

      {/* Period filter */}
      <div className="flex space-x-2">
        {periods.map((p) => (
          <button
            key={p.value}
            onClick={() => onPeriodChange(p.value)}
            className={`pill ${period === p.value ? 'pill-active' : 'pill-inactive'}`}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  )
}

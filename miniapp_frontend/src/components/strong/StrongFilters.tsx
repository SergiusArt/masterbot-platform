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
    <div className="card space-y-3">
      {/* Direction filter */}
      <div>
        <div className="text-xs text-tg-hint mb-1">Направление</div>
        <div className="flex space-x-2">
          {directions.map((d) => (
            <button
              key={d.value}
              onClick={() => onDirectionChange(d.value)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                filterDirection === d.value
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint'
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      {/* Period filter */}
      <div>
        <div className="text-xs text-tg-hint mb-1">Период</div>
        <div className="flex space-x-2">
          {periods.map((p) => (
            <button
              key={p.value}
              onClick={() => onPeriodChange(p.value)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                period === p.value
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

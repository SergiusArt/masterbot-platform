import { useImpulseStore } from '../../store/impulseStore'

const minPercentOptions = [10, 15, 20, 30, 50]

export function ImpulseFilters() {
  const { filterType, filterMinPercent, setFilterType, setFilterMinPercent } =
    useImpulseStore()

  return (
    <div className="card space-y-3">
      {/* Type filter */}
      <div>
        <div className="text-xs text-tg-hint mb-1">Тип</div>
        <div className="flex space-x-2">
          {(['all', 'growth', 'fall'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filterType === type
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint'
              }`}
            >
              {type === 'all' ? 'Все' : type === 'growth' ? '📈 Рост' : '📉 Падение'}
            </button>
          ))}
        </div>
      </div>

      {/* Min percent filter */}
      <div>
        <div className="text-xs text-tg-hint mb-1">Мин. процент</div>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setFilterMinPercent(null)}
            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
              filterMinPercent === null
                ? 'bg-tg-button text-tg-button-text'
                : 'bg-tg-secondary-bg text-tg-hint'
            }`}
          >
            Все
          </button>
          {minPercentOptions.map((percent) => (
            <button
              key={percent}
              onClick={() => setFilterMinPercent(percent)}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                filterMinPercent === percent
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint'
              }`}
            >
              ≥{percent}%
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

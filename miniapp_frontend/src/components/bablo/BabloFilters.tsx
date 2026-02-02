import { useBabloStore } from '../../store/babloStore'

const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h']

export function BabloFilters() {
  const { filterDirection, filterTimeframe, setFilterDirection, setFilterTimeframe } =
    useBabloStore()

  return (
    <div className="card space-y-3">
      {/* Direction filter */}
      <div>
        <div className="text-xs text-tg-hint mb-1">Направление</div>
        <div className="flex space-x-2">
          {(['all', 'long', 'short'] as const).map((dir) => (
            <button
              key={dir}
              onClick={() => setFilterDirection(dir)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filterDirection === dir
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint'
              }`}
            >
              {dir === 'all' ? 'Все' : dir.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Timeframe filter */}
      <div>
        <div className="text-xs text-tg-hint mb-1">Таймфрейм</div>
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setFilterTimeframe(null)}
            className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
              filterTimeframe === null
                ? 'bg-tg-button text-tg-button-text'
                : 'bg-tg-secondary-bg text-tg-hint'
            }`}
          >
            Все
          </button>
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setFilterTimeframe(tf)}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                filterTimeframe === tf
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

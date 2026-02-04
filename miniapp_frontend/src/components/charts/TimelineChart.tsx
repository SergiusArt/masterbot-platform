import { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { api } from '../../api'
import type { TimeSeriesPeriod, TimeSeriesData } from '../../types'

interface TimelineChartProps {
  service: 'impulse' | 'bablo'
  title: string
  color?: string
  height?: number
}

const periodLabels: Record<TimeSeriesPeriod, string> = {
  today: 'Сегодня',
  week: 'Неделя',
  month: 'Месяц',
}

export function TimelineChart({
  service,
  title,
  color = '#2481cc',
  height = 220,
}: TimelineChartProps) {
  const [period, setPeriod] = useState<TimeSeriesPeriod>('today')
  const [data, setData] = useState<TimeSeriesData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const result = await api.getTimeSeries(service, period)
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [service, period])

  // Transform data for chart
  const chartData = data
    ? data.labels.map((label, index) => ({
        label,
        count: data.counts[index],
      }))
    : []

  // Determine tick interval based on data length
  const getTickInterval = () => {
    if (!chartData.length) return 0
    if (period === 'today') {
      // Show every 3 hours
      return 2
    }
    if (period === 'week') {
      // Show all days
      return 0
    }
    // Month: show every 5 days
    return 4
  }

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <span>{title}</span>
        {data && (
          <span className="text-xs text-tg-hint font-normal">
            Всего: {data.total}
          </span>
        )}
      </div>

      {/* Period selector */}
      <div className="flex gap-2 px-4 pt-2">
        {(['today', 'week', 'month'] as TimeSeriesPeriod[]).map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-3 py-1.5 text-xs rounded-full transition-colors ${
              period === p
                ? 'bg-tg-button text-tg-button-text'
                : 'bg-tg-secondary-bg text-tg-hint hover:text-tg-text'
            }`}
          >
            {periodLabels[p]}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="p-4">
        {isLoading ? (
          <div
            className="flex items-center justify-center"
            style={{ height: height - 40 }}
          >
            <div className="animate-spin h-6 w-6 border-2 border-tg-button border-t-transparent rounded-full" />
          </div>
        ) : error ? (
          <div
            className="flex items-center justify-center text-tg-destructive text-sm"
            style={{ height: height - 40 }}
          >
            {error}
          </div>
        ) : chartData.length === 0 ? (
          <div
            className="flex items-center justify-center text-tg-hint text-sm"
            style={{ height: height - 40 }}
          >
            Нет данных
          </div>
        ) : (
          <div style={{ height: height - 40 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--tg-theme-hint-color, #e0e0e0)"
                  opacity={0.3}
                  vertical={false}
                />
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 9, fill: 'var(--tg-theme-hint-color, #999)' }}
                  tickLine={false}
                  axisLine={false}
                  interval={getTickInterval()}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: 'var(--tg-theme-hint-color, #999)' }}
                  tickLine={false}
                  axisLine={false}
                  width={30}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--tg-theme-section-bg-color, #fff)',
                    border: 'none',
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    fontSize: '12px',
                  }}
                  labelStyle={{ color: 'var(--tg-theme-text-color, #000)' }}
                  formatter={(value: number) => [value, 'Сигналов']}
                />
                {data && data.median > 0 && (
                  <ReferenceLine
                    y={data.median}
                    stroke="var(--tg-theme-hint-color, #999)"
                    strokeDasharray="5 5"
                    label={{
                      value: `Медиана: ${data.median}`,
                      position: 'right',
                      fontSize: 10,
                      fill: 'var(--tg-theme-hint-color, #999)',
                    }}
                  />
                )}
                <Bar
                  dataKey="count"
                  fill={color}
                  radius={[2, 2, 0, 0]}
                  maxBarSize={period === 'today' ? 20 : 30}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  )
}

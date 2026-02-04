import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { api } from '../../api'
import { LoadingSpinner } from '../common/LoadingSpinner'
import type { TimeSeriesPeriod } from '../../types'

interface ServiceAnalytics {
  period: string
  total_impulses?: number
  total_signals?: number
  growth_count?: number
  fall_count?: number
  long_count?: number
  short_count?: number
  average_quality?: number
  comparison?: {
    vs_yesterday?: string
    yesterday_total?: number
    vs_week_median?: string
    week_median?: number
    vs_month_median?: string
    month_median?: number
  }
  // For bablo
  vs_yesterday?: string
  vs_week_avg?: string
  today?: number
  yesterday?: number
  week_avg?: number
}

interface ReportData {
  impulses: ServiceAnalytics | null
  bablo: ServiceAnalytics | null
}

const periodLabels: Record<TimeSeriesPeriod | 'yesterday', string> = {
  today: 'Сегодня',
  yesterday: 'Вчера',
  week: 'Неделя',
  month: 'Месяц',
}

interface PieDataItem {
  name: string
  value: number
  color: string
}

function MiniPieChart({ data }: { data: PieDataItem[] }) {
  const total = data.reduce((sum, item) => sum + item.value, 0)

  if (total === 0) {
    return (
      <div className="text-center text-tg-hint text-sm py-4">
        Нет данных
      </div>
    )
  }

  return (
    <div className="flex items-center gap-4 w-full">
      <div className="w-24 h-24">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={25}
              outerRadius={40}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex-1 space-y-2">
        {data.map((item, index) => {
          const percent = total > 0 ? ((item.value / total) * 100).toFixed(0) : 0
          return (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-tg-text">{item.name}</span>
              </div>
              <div className="text-right">
                <span className="text-sm font-semibold" style={{ color: item.color }}>
                  {item.value}
                </span>
                <span className="text-xs text-tg-hint ml-1">({percent}%)</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function ReportsDashboard() {
  const [period, setPeriod] = useState<'today' | 'yesterday' | 'week' | 'month'>('today')
  const [data, setData] = useState<ReportData>({ impulses: null, bablo: null })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const [impulseData, babloData] = await Promise.all([
          api.getAnalytics('impulse', period),
          api.getAnalytics('bablo', period),
        ])
        setData({
          impulses: impulseData as unknown as ServiceAnalytics,
          bablo: babloData as unknown as ServiceAnalytics,
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [period])

  if (isLoading) {
    return <LoadingSpinner text="Загрузка отчётов..." />
  }

  if (error) {
    return (
      <div className="card m-4 text-center py-8">
        <span className="text-4xl">❌</span>
        <p className="mt-2 text-tg-destructive">{error}</p>
      </div>
    )
  }

  const impulseTotal = data.impulses?.total_impulses ?? 0
  const babloTotal = data.bablo?.total_signals ?? 0

  return (
    <div className="p-4 space-y-4">
      {/* Period selector */}
      <div className="card">
        <div className="card-header">Период</div>
        <div className="flex gap-2 p-4">
          {(['today', 'yesterday', 'week', 'month'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
                period === p
                  ? 'bg-tg-button text-tg-button-text'
                  : 'bg-tg-secondary-bg text-tg-hint hover:text-tg-text'
              }`}
            >
              {periodLabels[p]}
            </button>
          ))}
        </div>
      </div>

      {/* Impulses Report */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <span className="text-lg">⚡</span>
          <span>Импульсы</span>
        </div>
        <div className="p-4 space-y-4">
          {/* Total */}
          <div className="flex justify-between items-center">
            <span className="text-tg-hint">Всего сигналов</span>
            <span className="text-2xl font-bold text-tg-text">{impulseTotal}</span>
          </div>

          {/* Growth/Fall pie chart */}
          <div className="flex items-center justify-center">
            <MiniPieChart
              data={[
                { name: 'Рост', value: data.impulses?.growth_count ?? 0, color: '#22c55e' },
                { name: 'Падение', value: data.impulses?.fall_count ?? 0, color: '#ef4444' },
              ]}
            />
          </div>

          {/* Comparison */}
          {data.impulses?.comparison && (
            <div className="space-y-2 pt-2 border-t border-tg-hint/10">
              {data.impulses.comparison.vs_yesterday && (
                <div className="flex justify-between text-sm">
                  <span className="text-tg-hint">vs вчера</span>
                  <span className={getComparisonColor(data.impulses.comparison.vs_yesterday)}>
                    {data.impulses.comparison.vs_yesterday}
                  </span>
                </div>
              )}
              {data.impulses.comparison.week_median !== undefined && (
                <div className="flex justify-between text-sm">
                  <span className="text-tg-hint">Медиана недели</span>
                  <span className="text-tg-text">{data.impulses.comparison.week_median}</span>
                </div>
              )}
              {data.impulses.comparison.vs_week_median && (
                <div className="flex justify-between text-sm">
                  <span className="text-tg-hint">Активность</span>
                  <span className={getActivityColor(data.impulses.comparison.vs_week_median)}>
                    {data.impulses.comparison.vs_week_median}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Bablo Report */}
      <div className="card">
        <div className="card-header flex items-center gap-2">
          <span className="text-lg">💰</span>
          <span>Bablo</span>
        </div>
        <div className="p-4 space-y-4">
          {/* Total */}
          <div className="flex justify-between items-center">
            <span className="text-tg-hint">Всего сигналов</span>
            <span className="text-2xl font-bold text-tg-text">{babloTotal}</span>
          </div>

          {/* Long/Short pie chart */}
          <div className="flex items-center justify-center">
            <MiniPieChart
              data={[
                { name: 'Long', value: data.bablo?.long_count ?? 0, color: '#22c55e' },
                { name: 'Short', value: data.bablo?.short_count ?? 0, color: '#ef4444' },
              ]}
            />
          </div>

          {/* Average Quality */}
          {data.bablo?.average_quality !== undefined && data.bablo.average_quality !== null && (
            <div className="flex justify-between items-center">
              <span className="text-tg-hint">Среднее качество</span>
              <span className="text-lg font-semibold text-tg-text">
                {Number(data.bablo.average_quality).toFixed(1)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="card">
        <div className="card-header">Итого за {periodLabels[period].toLowerCase()}</div>
        <div className="p-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-tg-text">
                {impulseTotal + babloTotal}
              </div>
              <div className="text-xs text-tg-hint mt-1">всего сигналов</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-tg-link">
                {impulseTotal > 0 && babloTotal > 0
                  ? ((impulseTotal / babloTotal) * 100).toFixed(0)
                  : '--'}
                %
              </div>
              <div className="text-xs text-tg-hint mt-1">импульсов к Bablo</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function getComparisonColor(value: string): string {
  if (value.startsWith('+')) return 'text-green-500'
  if (value.startsWith('-')) return 'text-red-500'
  return 'text-tg-text'
}

function getActivityColor(value: string): string {
  if (value.includes('высокая')) return 'text-orange-500'
  if (value.includes('низкая')) return 'text-blue-500'
  if (value.includes('норме')) return 'text-green-500'
  return 'text-tg-hint'
}

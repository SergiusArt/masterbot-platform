/**
 * Active users chart component.
 */

import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import { adminApi } from '../../api/admin'
import type { DailyActivity } from '../../types/admin'

export function ActiveUsersChart() {
  const [data, setData] = useState<DailyActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getActivity(30)
      // Reverse to show oldest first (left to right)
      setData(response.daily_active_users.reverse())
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })
  }

  if (loading) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Активные пользователи</h3>
        <div className="h-40 bg-tg-secondary-bg rounded animate-pulse" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Активные пользователи</h3>
        <div className="text-center text-tg-hint py-8">{error}</div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Активные пользователи</h3>
        <div className="text-center text-tg-hint py-8">Нет данных</div>
      </div>
    )
  }

  return (
    <div className="card p-3 mb-4">
      <h3 className="font-semibold text-tg-text mb-3">Активные пользователи (30 дней)</h3>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fontSize: 10, fill: 'var(--tg-theme-hint-color)' }}
              axisLine={false}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--tg-theme-hint-color)' }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--tg-theme-bg-color)',
                border: '1px solid var(--tg-theme-hint-color)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelFormatter={formatDate}
              formatter={(value: number) => [value, 'Пользователей']}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="var(--tg-theme-button-color)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: 'var(--tg-theme-button-color)' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

/**
 * User activity frequency table.
 */

import { useEffect, useState } from 'react'
import { adminApi } from '../../api/admin'
import type { UserFrequency } from '../../types/admin'

export function UserActivityTable() {
  const [data, setData] = useState<UserFrequency[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const response = await adminApi.getActivity(30)
      setData(response.user_frequency)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Частота использования</h3>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse flex justify-between p-2">
              <div className="h-4 bg-tg-hint/20 rounded w-24" />
              <div className="h-4 bg-tg-hint/20 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Частота использования</h3>
        <div className="text-center text-tg-hint py-4">{error}</div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Частота использования</h3>
        <div className="text-center text-tg-hint py-4">Нет данных</div>
      </div>
    )
  }

  return (
    <div className="card p-3 mb-4">
      <h3 className="font-semibold text-tg-text mb-3">Частота использования (30 дней)</h3>
      <div className="max-h-[300px] overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-tg-bg">
            <tr className="text-tg-hint text-left">
              <th className="py-2">Пользователь</th>
              <th className="py-2 text-right">Визиты</th>
              <th className="py-2 text-right">Последний</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={item.user_id} className="border-t border-tg-hint/10">
                <td className="py-2">
                  <div className="flex items-center gap-2">
                    <span className="text-tg-hint text-xs w-4">{index + 1}</span>
                    <span className="text-tg-text truncate max-w-[100px]">
                      {item.first_name || item.username || `ID: ${item.user_id}`}
                    </span>
                  </div>
                </td>
                <td className="py-2 text-right">
                  <span className="px-2 py-0.5 bg-tg-button/10 text-tg-button rounded text-xs font-medium">
                    {item.visit_count}
                  </span>
                </td>
                <td className="py-2 text-right text-tg-hint text-xs">
                  {formatDate(item.last_visit)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

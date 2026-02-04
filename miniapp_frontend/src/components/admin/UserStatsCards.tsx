/**
 * User statistics cards component.
 */

import { useEffect, useState } from 'react'
import { adminApi } from '../../api/admin'
import type { UserStats } from '../../types/admin'

export function UserStatsCards() {
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const data = await adminApi.getStats()
      setStats(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-2 mb-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card p-3 animate-pulse">
            <div className="h-4 bg-tg-hint/20 rounded w-16 mb-2" />
            <div className="h-6 bg-tg-hint/20 rounded w-12" />
          </div>
        ))}
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="card p-3 mb-4 text-center text-tg-hint">
        {error || 'No data'}
      </div>
    )
  }

  const cards = [
    { label: 'Всего', value: stats.total_users, icon: '👥', color: 'text-tg-text' },
    { label: 'Активных', value: stats.active_users, icon: '✅', color: 'text-green-500' },
    { label: 'Истекает', value: stats.expiring_soon, icon: '⏰', color: 'text-yellow-500' },
    { label: 'Заблок.', value: stats.blocked_users, icon: '🚫', color: 'text-red-500' },
  ]

  return (
    <div className="grid grid-cols-2 gap-2 mb-4">
      {cards.map((card) => (
        <div key={card.label} className="card p-3">
          <div className="flex items-center gap-1.5 text-tg-hint text-xs mb-1">
            <span>{card.icon}</span>
            <span>{card.label}</span>
          </div>
          <div className={`text-xl font-bold ${card.color}`}>{card.value}</div>
        </div>
      ))}
    </div>
  )
}

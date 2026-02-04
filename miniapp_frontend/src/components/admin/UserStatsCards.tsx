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
      <div className="grid grid-cols-5 gap-1.5 mb-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="card p-2 animate-pulse text-center">
            <div className="h-3 bg-tg-hint/20 rounded w-4 mx-auto mb-1" />
            <div className="h-5 bg-tg-hint/20 rounded w-6 mx-auto mb-1" />
            <div className="h-2 bg-tg-hint/20 rounded w-8 mx-auto" />
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
    { label: 'Истёк', value: stats.expired_users, icon: '💀', color: 'text-red-500' },
    { label: 'Истекает', value: stats.expiring_soon, icon: '⏰', color: 'text-yellow-500' },
    { label: 'Заблок.', value: stats.blocked_users, icon: '🚫', color: 'text-tg-hint' },
  ]

  return (
    <div className="grid grid-cols-5 gap-1.5 mb-4">
      {cards.map((card) => (
        <div key={card.label} className="card p-2 text-center">
          <div className="text-xs mb-0.5">{card.icon}</div>
          <div className={`text-lg font-bold ${card.color}`}>{card.value}</div>
          <div className="text-tg-hint text-[10px]">{card.label}</div>
        </div>
      ))}
    </div>
  )
}

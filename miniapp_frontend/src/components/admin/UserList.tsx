/**
 * User list component with search and actions.
 */

import { useEffect, useState, useCallback } from 'react'
import { adminApi } from '../../api/admin'
import type { AdminUser } from '../../types/admin'

interface UserListProps {
  onEdit: (user: AdminUser) => void
  onAdd: () => void
  refreshTrigger?: number
}

export function UserList({ onEdit, onAdd, refreshTrigger }: UserListProps) {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true)
      const data = await adminApi.getUsers({ search: search || undefined, limit: 50 })
      setUsers(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => {
    loadUsers()
  }, [loadUsers, refreshTrigger])

  // Debounced search
  useEffect(() => {
    const timeout = setTimeout(() => {
      loadUsers()
    }, 300)
    return () => clearTimeout(timeout)
  }, [search, loadUsers])

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: '2-digit' })
  }

  const getStatusBadge = (user: AdminUser) => {
    if (!user.is_active) {
      return <span className="px-1.5 py-0.5 bg-red-500/20 text-red-500 rounded text-xs">Заблок.</span>
    }
    if (user.access_expires_at) {
      const expires = new Date(user.access_expires_at)
      const now = new Date()
      const daysLeft = Math.ceil((expires.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
      if (daysLeft <= 0) {
        return <span className="px-1.5 py-0.5 bg-red-500/20 text-red-500 rounded text-xs">Истёк</span>
      }
      if (daysLeft <= 7) {
        return <span className="px-1.5 py-0.5 bg-yellow-500/20 text-yellow-500 rounded text-xs">{daysLeft}д</span>
      }
    }
    return <span className="px-1.5 py-0.5 bg-green-500/20 text-green-500 rounded text-xs">Актив.</span>
  }

  return (
    <div className="card p-3 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-tg-text">Пользователи</h3>
        <button
          onClick={onAdd}
          className="px-3 py-1.5 bg-tg-button text-tg-button-text rounded-lg text-sm font-medium"
        >
          + Добавить
        </button>
      </div>

      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Поиск по ID, username..."
        className="w-full px-3 py-2 bg-tg-secondary-bg rounded-lg text-tg-text text-sm mb-3 outline-none focus:ring-1 focus:ring-tg-button"
      />

      {loading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse flex items-center gap-3 p-2">
              <div className="w-10 h-10 bg-tg-hint/20 rounded-full" />
              <div className="flex-1">
                <div className="h-4 bg-tg-hint/20 rounded w-24 mb-1" />
                <div className="h-3 bg-tg-hint/20 rounded w-16" />
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center text-tg-hint py-4">{error}</div>
      ) : users.length === 0 ? (
        <div className="text-center text-tg-hint py-4">Пользователи не найдены</div>
      ) : (
        <div className="space-y-1 max-h-[400px] overflow-y-auto">
          {users.map((user) => (
            <button
              key={user.id}
              onClick={() => onEdit(user)}
              className="w-full flex items-center gap-3 p-2 hover:bg-tg-secondary-bg rounded-lg transition-colors text-left"
            >
              <div className="w-10 h-10 bg-tg-button/20 rounded-full flex items-center justify-center text-tg-button font-medium">
                {user.first_name?.[0] || user.username?.[0] || '?'}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-tg-text truncate">
                    {user.first_name || user.username || `ID: ${user.id}`}
                  </span>
                  {user.is_admin && <span className="text-xs">👑</span>}
                </div>
                <div className="text-xs text-tg-hint truncate">
                  @{user.username || '-'} | {user.id}
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                {getStatusBadge(user)}
                <span className="text-xs text-tg-hint">
                  {formatDate(user.last_activity)}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

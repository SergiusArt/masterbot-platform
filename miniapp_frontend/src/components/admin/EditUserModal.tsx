/**
 * Modal for editing user.
 */

import { useState } from 'react'
import { adminApi } from '../../api/admin'
import type { AdminUser } from '../../types/admin'

interface EditUserModalProps {
  user: AdminUser | null
  onClose: () => void
  onSuccess: () => void
}

export function EditUserModal({ user, onClose, onSuccess }: EditUserModalProps) {
  const [extendDays, setExtendDays] = useState('30')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!user) return null

  const handleExtend = async () => {
    const days = parseInt(extendDays, 10)
    if (isNaN(days) || days < 0) {
      setError('Введите корректное количество дней')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await adminApi.updateUser(user.id, { extend_days: days })
      onSuccess()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async () => {
    try {
      setLoading(true)
      setError(null)
      await adminApi.updateUser(user.id, { is_active: !user.is_active })
      onSuccess()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleAdmin = async () => {
    try {
      setLoading(true)
      setError(null)
      await adminApi.updateUser(user.id, { is_admin: !user.is_admin })
      onSuccess()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Безлимит'
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-tg-bg w-full sm:max-w-md rounded-t-2xl sm:rounded-2xl p-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-tg-text">
            {user.first_name || user.username || `ID: ${user.id}`}
            {user.is_admin && ' 👑'}
          </h2>
          <button onClick={onClose} className="text-tg-hint text-2xl leading-none">&times;</button>
        </div>

        {/* User info */}
        <div className="card p-3 mb-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-tg-hint">Telegram ID:</span>
            <span className="text-tg-text font-mono">{user.id}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-tg-hint">Username:</span>
            <span className="text-tg-text">@{user.username || '-'}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-tg-hint">Статус:</span>
            <span className={user.is_active ? 'text-green-500' : 'text-red-500'}>
              {user.is_active ? 'Активен' : 'Заблокирован'}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-tg-hint">Доступ до:</span>
            <span className="text-tg-text">{formatDate(user.access_expires_at)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-tg-hint">Последняя активность:</span>
            <span className="text-tg-text">{formatDate(user.last_activity)}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          {/* Extend access */}
          <div className="card p-3">
            <div className="text-sm text-tg-hint mb-2">Продлить доступ</div>
            <div className="flex gap-2">
              <input
                type="number"
                value={extendDays}
                onChange={(e) => setExtendDays(e.target.value)}
                placeholder="Дней"
                min="0"
                className="flex-1 px-3 py-2 bg-tg-secondary-bg rounded-lg text-tg-text text-sm outline-none"
              />
              <button
                onClick={handleExtend}
                disabled={loading}
                className="px-4 py-2 bg-tg-button text-tg-button-text rounded-lg text-sm font-medium disabled:opacity-50"
              >
                +{extendDays}д
              </button>
            </div>
            <div className="text-xs text-tg-hint mt-1">0 = безлимитный доступ</div>
          </div>

          {/* Toggle active */}
          <button
            onClick={handleToggleActive}
            disabled={loading}
            className={`w-full p-3 rounded-xl text-sm font-medium disabled:opacity-50 ${
              user.is_active
                ? 'bg-red-500/10 text-red-500'
                : 'bg-green-500/10 text-green-500'
            }`}
          >
            {user.is_active ? '🚫 Заблокировать' : '✅ Разблокировать'}
          </button>

          {/* Toggle admin */}
          <button
            onClick={handleToggleAdmin}
            disabled={loading}
            className={`w-full p-3 rounded-xl text-sm font-medium disabled:opacity-50 ${
              user.is_admin
                ? 'bg-yellow-500/10 text-yellow-500'
                : 'bg-tg-button/10 text-tg-button'
            }`}
          >
            {user.is_admin ? '👤 Убрать админа' : '👑 Сделать админом'}
          </button>

          {error && (
            <div className="p-3 bg-red-500/10 text-red-500 rounded-lg text-sm">
              {error}
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="w-full mt-4 px-4 py-3 bg-tg-secondary-bg text-tg-text rounded-xl font-medium"
        >
          Закрыть
        </button>
      </div>
    </div>
  )
}

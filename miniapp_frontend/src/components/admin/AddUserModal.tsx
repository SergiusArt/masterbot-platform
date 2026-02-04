/**
 * Modal for adding a new user.
 */

import { useState } from 'react'
import { adminApi } from '../../api/admin'

interface AddUserModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export function AddUserModal({ isOpen, onClose, onSuccess }: AddUserModalProps) {
  const [userId, setUserId] = useState('')
  const [days, setDays] = useState('30')
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const userIdNum = parseInt(userId, 10)
    if (isNaN(userIdNum) || userIdNum <= 0) {
      setError('Введите корректный Telegram ID')
      return
    }

    const daysNum = parseInt(days, 10)
    if (isNaN(daysNum) || daysNum < 0) {
      setError('Введите корректное количество дней (0 = безлимит)')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await adminApi.addUser({
        user_id: userIdNum,
        days: daysNum,
        username: username || undefined,
      })
      onSuccess()
      handleClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add user')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setUserId('')
    setDays('30')
    setUsername('')
    setError(null)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div className="relative bg-tg-bg w-full sm:max-w-md rounded-t-2xl sm:rounded-2xl p-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-tg-text">Добавить пользователя</h2>
          <button onClick={handleClose} className="text-tg-hint text-2xl leading-none">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-tg-hint mb-1">Telegram ID *</label>
            <input
              type="number"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="123456789"
              className="w-full px-3 py-2 bg-tg-secondary-bg rounded-lg text-tg-text outline-none focus:ring-1 focus:ring-tg-button"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-tg-hint mb-1">Username (опционально)</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="@username"
              className="w-full px-3 py-2 bg-tg-secondary-bg rounded-lg text-tg-text outline-none focus:ring-1 focus:ring-tg-button"
            />
          </div>

          <div>
            <label className="block text-sm text-tg-hint mb-1">Дней доступа (0 = безлимит)</label>
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(e.target.value)}
              placeholder="30"
              min="0"
              className="w-full px-3 py-2 bg-tg-secondary-bg rounded-lg text-tg-text outline-none focus:ring-1 focus:ring-tg-button"
            />
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 text-red-500 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-3 bg-tg-secondary-bg text-tg-text rounded-xl font-medium"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-3 bg-tg-button text-tg-button-text rounded-xl font-medium disabled:opacity-50"
            >
              {loading ? 'Добавление...' : 'Добавить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

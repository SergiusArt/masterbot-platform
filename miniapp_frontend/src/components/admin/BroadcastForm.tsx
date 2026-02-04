/**
 * Broadcast message form component.
 */

import { useEffect, useState } from 'react'
import { adminApi } from '../../api/admin'
import type { BroadcastHistoryItem } from '../../types/admin'

export function BroadcastForm() {
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [history, setHistory] = useState<BroadcastHistoryItem[]>([])
  const [loadingHistory, setLoadingHistory] = useState(true)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      setLoadingHistory(true)
      const data = await adminApi.getBroadcastHistory(10)
      setHistory(data)
    } catch (err) {
      console.error('Failed to load broadcast history:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  const handleSend = async () => {
    if (!message.trim()) {
      setError('Введите сообщение')
      return
    }

    try {
      setSending(true)
      setError(null)
      setSuccess(null)
      const result = await adminApi.sendBroadcast({ message: message.trim() })
      setSuccess(`Отправлено ${result.sent_to} пользователям`)
      setMessage('')
      loadHistory()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send broadcast')
    } finally {
      setSending(false)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="space-y-4">
      {/* Send form */}
      <div className="card p-3">
        <h3 className="font-semibold text-tg-text mb-3">Рассылка сообщений</h3>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Введите сообщение для рассылки..."
          className="w-full px-3 py-2 bg-tg-secondary-bg rounded-lg text-tg-text text-sm outline-none focus:ring-1 focus:ring-tg-button resize-none h-24"
        />
        <div className="text-xs text-tg-hint mt-1 mb-3">
          Сообщение будет отправлено всем активным пользователям
        </div>

        {error && (
          <div className="p-2 bg-red-500/10 text-red-500 rounded-lg text-sm mb-3">
            {error}
          </div>
        )}

        {success && (
          <div className="p-2 bg-green-500/10 text-green-500 rounded-lg text-sm mb-3">
            {success}
          </div>
        )}

        <button
          onClick={handleSend}
          disabled={sending || !message.trim()}
          className="w-full px-4 py-3 bg-tg-button text-tg-button-text rounded-xl font-medium disabled:opacity-50"
        >
          {sending ? 'Отправка...' : 'Отправить всем'}
        </button>
      </div>

      {/* History */}
      <div className="card p-3">
        <h3 className="font-semibold text-tg-text mb-3">История рассылок</h3>
        {loadingHistory ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div key={i} className="animate-pulse p-2 bg-tg-secondary-bg rounded-lg">
                <div className="h-4 bg-tg-hint/20 rounded w-3/4 mb-2" />
                <div className="h-3 bg-tg-hint/20 rounded w-1/4" />
              </div>
            ))}
          </div>
        ) : history.length === 0 ? (
          <div className="text-center text-tg-hint py-4">Нет рассылок</div>
        ) : (
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {history.map((item) => (
              <div key={item.id} className="p-2 bg-tg-secondary-bg rounded-lg">
                <div className="text-sm text-tg-text line-clamp-2">{item.message}</div>
                <div className="flex items-center justify-between mt-1 text-xs text-tg-hint">
                  <span>{formatDate(item.created_at)}</span>
                  <span>{item.sent_to} получателей</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

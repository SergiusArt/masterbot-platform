/**
 * Service health status component.
 */

import { useEffect, useState } from 'react'
import { adminApi } from '../../api/admin'
import type { ServiceStatus } from '../../types/admin'

export function ServiceHealth() {
  const [services, setServices] = useState<ServiceStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadServices()
  }, [])

  const loadServices = async () => {
    try {
      setLoading(true)
      const data = await adminApi.getServices()
      setServices(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load services')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card p-3 mb-4">
        <h3 className="font-semibold text-tg-text mb-3">Статус сервисов</h3>
        <div className="space-y-2">
          {[1, 2].map((i) => (
            <div key={i} className="animate-pulse flex items-center justify-between p-3 bg-tg-secondary-bg rounded-lg">
              <div className="h-4 bg-tg-hint/20 rounded w-24" />
              <div className="h-6 bg-tg-hint/20 rounded w-16" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-3 mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-tg-text">Статус сервисов</h3>
          <button onClick={loadServices} className="text-tg-button text-sm">
            Обновить
          </button>
        </div>
        <div className="text-center text-tg-hint py-4">{error}</div>
      </div>
    )
  }

  return (
    <div className="card p-3 mb-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-tg-text">Статус сервисов</h3>
        <button onClick={loadServices} className="text-tg-button text-sm">
          Обновить
        </button>
      </div>
      <div className="space-y-2">
        {services.map((service) => (
          <div
            key={service.name}
            className="flex items-center justify-between p-3 bg-tg-secondary-bg rounded-lg"
          >
            <div>
              <div className="font-medium text-tg-text">{service.display_name}</div>
              {service.latency_ms !== null && service.latency_ms !== undefined && (
                <div className="text-xs text-tg-hint">{service.latency_ms}ms</div>
              )}
              {service.error && (
                <div className="text-xs text-red-500 truncate max-w-[200px]">{service.error}</div>
              )}
            </div>
            <div
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                service.status === 'healthy'
                  ? 'bg-green-500/20 text-green-500'
                  : 'bg-red-500/20 text-red-500'
              }`}
            >
              {service.status === 'healthy' ? '✓ OK' : '✗ Ошибка'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

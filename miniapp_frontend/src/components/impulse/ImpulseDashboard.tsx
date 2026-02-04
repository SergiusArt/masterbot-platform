import { useEffect } from 'react'
import { useImpulseStore, selectFilteredImpulses } from '../../store/impulseStore'
import { api } from '../../api'
import { ImpulseStats } from './ImpulseStats'
import { ImpulseList } from './ImpulseList'
import { ImpulseFilters } from './ImpulseFilters'
import { TimelineChart } from '../charts/TimelineChart'
import { LoadingSpinner } from '../common/LoadingSpinner'

export function ImpulseDashboard() {
  const { stats, isLoading, error, setImpulses, setStats, setLoading, setError } =
    useImpulseStore()
  const filteredImpulses = useImpulseStore(selectFilteredImpulses)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Fetch summary and impulses in parallel
        const [summaryData, impulsesData] = await Promise.all([
          api.getSummary(),
          api.getImpulses({ limit: 20 }),
        ])

        setStats(summaryData.impulses)
        setImpulses(impulsesData.impulses || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      }
    }

    fetchData()
  }, [setImpulses, setStats, setLoading, setError])

  if (isLoading && filteredImpulses.length === 0) {
    return <LoadingSpinner text="Загрузка импульсов..." />
  }

  if (error && filteredImpulses.length === 0) {
    return (
      <div className="card text-center py-8">
        <span className="text-4xl">❌</span>
        <p className="mt-2 text-tg-destructive">{error}</p>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      {stats && <ImpulseStats stats={stats} />}

      <TimelineChart
        service="impulse"
        title="Динамика импульсов"
        color="#22c55e"
      />

      <ImpulseFilters />

      <div className="card">
        <div className="card-header">Последние импульсы</div>
        <ImpulseList impulses={filteredImpulses} />
      </div>
    </div>
  )
}

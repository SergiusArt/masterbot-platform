import { useEffect } from 'react'
import { useBabloStore, selectFilteredSignals } from '../../store/babloStore'
import { api } from '../../api'
import { BabloStats } from './BabloStats'
import { BabloList } from './BabloList'
import { BabloFilters } from './BabloFilters'
import { TimelineChart } from '../charts/TimelineChart'
import { LoadingSpinner } from '../common/LoadingSpinner'

export function BabloDashboard() {
  const { stats, isLoading, error, setSignals, setStats, setLoading, setError } =
    useBabloStore()
  const filteredSignals = useBabloStore(selectFilteredSignals)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Fetch summary and signals in parallel
        const [summaryData, signalsData] = await Promise.all([
          api.getSummary(),
          api.getBabloSignals({ limit: 20 }),
        ])

        setStats(summaryData.bablo)
        setSignals(signalsData.signals || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      }
    }

    fetchData()
  }, [setSignals, setStats, setLoading, setError])

  if (isLoading && filteredSignals.length === 0) {
    return <LoadingSpinner text="Загрузка сигналов..." />
  }

  if (error && filteredSignals.length === 0) {
    return (
      <div className="card text-center py-8">
        <span className="text-4xl">❌</span>
        <p className="mt-2 text-tg-destructive">{error}</p>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      {stats && <BabloStats stats={stats} />}

      <TimelineChart
        service="bablo"
        title="Динамика сигналов"
        color="#3b82f6"
      />

      <BabloFilters />

      <div className="card">
        <div className="card-header">Последние сигналы</div>
        <BabloList signals={filteredSignals} />
      </div>
    </div>
  )
}

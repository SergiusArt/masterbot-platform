import { useEffect, useCallback } from 'react'
import { api } from '../../api'
import { useStrongStore, selectFilteredSignals, selectStrongSignals } from '../../store/strongStore'
import type { StrongPeriod } from '../../store/strongStore'
import { StrongStats } from './StrongStats'
import { StrongFilters } from './StrongFilters'
import { StrongSignalList } from './StrongSignalList'
import { ProfitDistributionChart } from './ProfitDistributionChart'
import { SignalPerformanceChart } from './SignalPerformanceChart'
import { LoadingSpinner } from '../common/LoadingSpinner'

function getPeriodDates(period: StrongPeriod): { from_date?: string; to_date?: string } {
  const now = new Date()

  if (period === 'current_month') {
    const from = new Date(now.getFullYear(), now.getMonth(), 1)
    return {
      from_date: from.toISOString(),
      to_date: now.toISOString(),
    }
  }

  if (period === 'prev_month') {
    const from = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const to = new Date(now.getFullYear(), now.getMonth(), 1)
    return {
      from_date: from.toISOString(),
      to_date: to.toISOString(),
    }
  }

  // 'all' - no date filter
  return {}
}

export function StrongDashboard() {
  const {
    stats,
    period,
    filterDirection,
    isLoading,
    error,
    setSignals,
    setStats,
    setFilterDirection,
    setPeriod,
    setLoading,
    setError,
  } = useStrongStore()

  const allSignals = useStrongStore(selectStrongSignals)
  const filteredSignals = useStrongStore(selectFilteredSignals)

  const fetchData = useCallback(async (currentPeriod: StrongPeriod) => {
    setLoading(true)
    try {
      const dates = getPeriodDates(currentPeriod)

      const [statsData, signalsData] = await Promise.all([
        api.getStrongStats(dates),
        api.getStrongSignals({ ...dates, limit: 100 }),
      ])

      setStats(statsData)
      setSignals(signalsData.signals)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    }
  }, [setSignals, setStats, setLoading, setError])

  useEffect(() => {
    fetchData(period)
  }, [period, fetchData])

  const handlePeriodChange = useCallback((newPeriod: StrongPeriod) => {
    setPeriod(newPeriod)
  }, [setPeriod])

  if (isLoading && !stats) {
    return <LoadingSpinner text="Загрузка..." />
  }

  if (error && !stats) {
    return (
      <div className="card m-4 text-center py-8">
        <span className="text-4xl">❌</span>
        <p className="mt-2 text-tg-destructive">{error}</p>
      </div>
    )
  }

  return (
    <div className="p-4 space-y-4">
      {/* Stats cards */}
      {stats && <StrongStats stats={stats} />}

      {/* Charts */}
      {stats && allSignals.length > 0 && (
        <>
          <ProfitDistributionChart
            signals={allSignals}
            avgProfit={stats.avg_profit_pct}
          />
          <SignalPerformanceChart
            signals={allSignals}
            avgProfit={stats.avg_profit_pct}
          />
        </>
      )}

      {/* Filters */}
      <StrongFilters
        filterDirection={filterDirection}
        period={period}
        onDirectionChange={setFilterDirection}
        onPeriodChange={handlePeriodChange}
      />

      {/* Signal list */}
      <StrongSignalList signals={filteredSignals} />
    </div>
  )
}

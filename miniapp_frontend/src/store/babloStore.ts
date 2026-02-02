import { create } from 'zustand'
import type { BabloSignal, BabloStats } from '../types'

interface BabloState {
  // Data
  signals: BabloSignal[]
  stats: BabloStats | null

  // Filters
  filterDirection: 'all' | 'long' | 'short'
  filterTimeframe: string | null
  filterMinQuality: number

  // Loading states
  isLoading: boolean
  error: string | null

  // Actions
  setSignals: (signals: BabloSignal[]) => void
  addSignal: (signal: BabloSignal) => void
  setStats: (stats: BabloStats) => void
  setFilterDirection: (direction: 'all' | 'long' | 'short') => void
  setFilterTimeframe: (timeframe: string | null) => void
  setFilterMinQuality: (quality: number) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const MAX_SIGNALS = 100

export const useBabloStore = create<BabloState>((set) => ({
  signals: [],
  stats: null,
  filterDirection: 'all',
  filterTimeframe: null,
  filterMinQuality: 0,
  isLoading: false,
  error: null,

  setSignals: (signals) =>
    set({ signals: signals.slice(0, MAX_SIGNALS), isLoading: false }),

  addSignal: (signal) =>
    set((state) => ({
      signals: [signal, ...state.signals].slice(0, MAX_SIGNALS),
      // Update stats if available
      stats: state.stats
        ? {
            ...state.stats,
            today_count: state.stats.today_count + 1,
            long_count:
              signal.direction === 'long'
                ? state.stats.long_count + 1
                : state.stats.long_count,
            short_count:
              signal.direction === 'short'
                ? state.stats.short_count + 1
                : state.stats.short_count,
          }
        : null,
    })),

  setStats: (stats) => set({ stats }),

  setFilterDirection: (filterDirection) => set({ filterDirection }),

  setFilterTimeframe: (filterTimeframe) => set({ filterTimeframe }),

  setFilterMinQuality: (filterMinQuality) => set({ filterMinQuality }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  reset: () =>
    set({
      signals: [],
      stats: null,
      filterDirection: 'all',
      filterTimeframe: null,
      filterMinQuality: 0,
      isLoading: false,
      error: null,
    }),
}))

// Selectors
export const selectBabloSignals = (state: BabloState) => state.signals
export const selectBabloStats = (state: BabloState) => state.stats
export const selectBabloLoading = (state: BabloState) => state.isLoading
export const selectBabloError = (state: BabloState) => state.error

export const selectFilteredSignals = (state: BabloState) => {
  let filtered = state.signals

  if (state.filterDirection !== 'all') {
    filtered = filtered.filter((s) => s.direction === state.filterDirection)
  }

  if (state.filterTimeframe) {
    filtered = filtered.filter((s) => s.timeframe === state.filterTimeframe)
  }

  if (state.filterMinQuality > 0) {
    filtered = filtered.filter((s) => s.quality_total >= state.filterMinQuality)
  }

  return filtered
}

export const selectLongSignals = (state: BabloState) =>
  state.signals.filter((s) => s.direction === 'long')
export const selectShortSignals = (state: BabloState) =>
  state.signals.filter((s) => s.direction === 'short')

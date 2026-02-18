import { create } from 'zustand'
import type { StrongSignal, StrongStats } from '../types'

export type StrongPeriod = 'current_month' | 'prev_month' | 'all'

interface StrongState {
  // Data
  signals: StrongSignal[]
  stats: StrongStats | null

  // Filters
  filterDirection: 'all' | 'long' | 'short'
  period: StrongPeriod

  // Loading states
  isLoading: boolean
  error: string | null

  // Actions
  setSignals: (signals: StrongSignal[]) => void
  addSignal: (signal: StrongSignal) => void
  setStats: (stats: StrongStats) => void
  setFilterDirection: (direction: 'all' | 'long' | 'short') => void
  setPeriod: (period: StrongPeriod) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

const MAX_SIGNALS = 200

export const useStrongStore = create<StrongState>((set) => ({
  signals: [],
  stats: null,
  filterDirection: 'all',
  period: 'current_month',
  isLoading: false,
  error: null,

  setSignals: (signals) =>
    set({ signals: signals.slice(0, MAX_SIGNALS), isLoading: false }),

  addSignal: (signal) =>
    set((state) => ({
      signals: [signal, ...state.signals].slice(0, MAX_SIGNALS),
    })),

  setStats: (stats) => set({ stats }),

  setFilterDirection: (filterDirection) => set({ filterDirection }),

  setPeriod: (period) => set({ period }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  reset: () =>
    set({
      signals: [],
      stats: null,
      filterDirection: 'all',
      period: 'current_month',
      isLoading: false,
      error: null,
    }),
}))

// Selectors
export const selectStrongSignals = (state: StrongState) => state.signals
export const selectStrongStats = (state: StrongState) => state.stats
export const selectStrongLoading = (state: StrongState) => state.isLoading
export const selectStrongError = (state: StrongState) => state.error

export const selectFilteredSignals = (state: StrongState) => {
  let filtered = state.signals

  if (state.filterDirection !== 'all') {
    filtered = filtered.filter((s) => s.direction === state.filterDirection)
  }

  return filtered
}

export const selectLongSignals = (state: StrongState) =>
  state.signals.filter((s) => s.direction === 'long')
export const selectShortSignals = (state: StrongState) =>
  state.signals.filter((s) => s.direction === 'short')

import { create } from 'zustand'
import type { Impulse, ImpulseStats } from '../types'

type ImpulseTypeFilter = 'all' | 'growth' | 'fall'

interface ImpulseState {
  // Data
  impulses: Impulse[]
  stats: ImpulseStats | null

  // Filters
  filterType: ImpulseTypeFilter
  filterMinPercent: number | null

  // Loading states
  isLoading: boolean
  error: string | null

  // Actions
  setImpulses: (impulses: Impulse[]) => void
  addImpulse: (impulse: Impulse) => void
  setStats: (stats: ImpulseStats) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setFilterType: (type: ImpulseTypeFilter) => void
  setFilterMinPercent: (percent: number | null) => void
  reset: () => void
}

const MAX_IMPULSES = 100

export const useImpulseStore = create<ImpulseState>((set) => ({
  impulses: [],
  stats: null,
  filterType: 'all',
  filterMinPercent: null,
  isLoading: false,
  error: null,

  setImpulses: (impulses) =>
    set({ impulses: impulses.slice(0, MAX_IMPULSES), isLoading: false }),

  addImpulse: (impulse) =>
    set((state) => ({
      impulses: [impulse, ...state.impulses].slice(0, MAX_IMPULSES),
      // Update stats if available
      stats: state.stats
        ? {
            ...state.stats,
            today_count: state.stats.today_count + 1,
            growth_count:
              impulse.type === 'growth'
                ? state.stats.growth_count + 1
                : state.stats.growth_count,
            fall_count:
              impulse.type === 'fall'
                ? state.stats.fall_count + 1
                : state.stats.fall_count,
          }
        : null,
    })),

  setStats: (stats) => set({ stats }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error, isLoading: false }),

  setFilterType: (filterType) => set({ filterType }),

  setFilterMinPercent: (filterMinPercent) => set({ filterMinPercent }),

  reset: () =>
    set({
      impulses: [],
      stats: null,
      filterType: 'all',
      filterMinPercent: null,
      isLoading: false,
      error: null,
    }),
}))

// Selectors
export const selectImpulses = (state: ImpulseState) => state.impulses
export const selectImpulseStats = (state: ImpulseState) => state.stats
export const selectImpulsesLoading = (state: ImpulseState) => state.isLoading
export const selectImpulsesError = (state: ImpulseState) => state.error

export const selectFilteredImpulses = (state: ImpulseState) => {
  let filtered = state.impulses

  // Filter by type
  if (state.filterType !== 'all') {
    filtered = filtered.filter((i) => i.type === state.filterType)
  }

  // Filter by min percent
  if (state.filterMinPercent !== null) {
    filtered = filtered.filter((i) => {
      const percent = typeof i.percent === 'string' ? parseFloat(i.percent) : i.percent
      return percent >= state.filterMinPercent!
    })
  }

  return filtered
}

export const selectGrowthImpulses = (state: ImpulseState) =>
  state.impulses.filter((i) => i.type === 'growth')
export const selectFallImpulses = (state: ImpulseState) =>
  state.impulses.filter((i) => i.type === 'fall')

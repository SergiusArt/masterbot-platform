import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'
import type { StrongSignal } from '../../types'

interface ProfitDistributionChartProps {
  signals: StrongSignal[]
  avgProfit: number
}

interface BinData {
  range: string
  count: number
  isAvgBin: boolean
}

/**
 * Profit distribution histogram.
 * Book principle: histogram for distribution data, equal intervals,
 * direct labeling, minimal gridlines, accent color for key insight.
 */
export function ProfitDistributionChart({ signals, avgProfit }: ProfitDistributionChartProps) {
  const { bins, maxCount } = useMemo(() => {
    // Only signals with calculated profit
    const calculated = signals.filter((s) => s.max_profit_pct != null)
    if (calculated.length === 0) return { bins: [], maxCount: 0 }

    const profits = calculated.map((s) => s.max_profit_pct!)

    // Determine bin size based on data range
    const min = Math.min(...profits)
    const max = Math.max(...profits)
    const range = max - min

    // Choose bin size: aim for 5-8 bins (book: test interval sizes)
    let binSize: number
    if (range <= 5) binSize = 1
    else if (range <= 15) binSize = 2
    else if (range <= 30) binSize = 5
    else binSize = 10

    // Create bins from floor(min) to ceil(max)
    const binStart = Math.floor(min / binSize) * binSize
    const binEnd = Math.ceil(max / binSize) * binSize

    const result: BinData[] = []
    for (let start = binStart; start < binEnd; start += binSize) {
      const end = start + binSize
      const count = profits.filter((p) => p >= start && p < end).length
      const isAvgBin = avgProfit >= start && avgProfit < end
      result.push({
        range: `${start}–${end}%`,
        count,
        isAvgBin,
      })
    }

    // Last bin includes upper bound
    if (result.length > 0) {
      const lastBin = result[result.length - 1]
      const lastStart = binEnd - binSize
      lastBin.count = profits.filter((p) => p >= lastStart && p <= binEnd).length
    }

    return {
      bins: result,
      maxCount: Math.max(...result.map((b) => b.count)),
    }
  }, [signals, avgProfit])

  if (bins.length === 0) {
    return null
  }

  return (
    <div className="card">
      <div className="card-header">Распределение профита по сигналам</div>
      <div className="px-1 pt-1" style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={bins}
            margin={{ top: 8, right: 8, left: -20, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--tg-theme-hint-color, #e0e0e0)"
              opacity={0.2}
              vertical={false}
            />
            <XAxis
              dataKey="range"
              tick={{ fontSize: 9, fill: 'var(--tg-theme-hint-color, #999)' }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: 'var(--tg-theme-hint-color, #999)' }}
              tickLine={false}
              axisLine={false}
              width={28}
              allowDecimals={false}
              domain={[0, maxCount + 1]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--tg-theme-section-bg-color, #fff)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                fontSize: '12px',
              }}
              labelStyle={{ color: 'var(--tg-theme-text-color, #000)' }}
              formatter={(value: number) => [value, 'Сигналов']}
            />
            {avgProfit > 0 && (
              <ReferenceLine
                x={bins.find((b) => b.isAvgBin)?.range}
                stroke="var(--tg-theme-accent-text-color, #2481cc)"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                label={{
                  value: `Avg ${avgProfit.toFixed(1)}%`,
                  position: 'top',
                  fontSize: 10,
                  fill: 'var(--tg-theme-accent-text-color, #2481cc)',
                }}
              />
            )}
            <Bar dataKey="count" radius={[3, 3, 0, 0]} maxBarSize={40}>
              {bins.map((entry, index) => (
                <Cell
                  key={index}
                  fill={
                    entry.isAvgBin
                      ? 'var(--tg-theme-accent-text-color, #2481cc)'
                      : 'var(--tg-theme-button-color, #2481cc)'
                  }
                  opacity={entry.isAvgBin ? 1 : 0.5}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="text-center text-xs text-tg-hint mt-1 pb-1">
        Выделен диапазон со средним профитом
      </div>
    </div>
  )
}

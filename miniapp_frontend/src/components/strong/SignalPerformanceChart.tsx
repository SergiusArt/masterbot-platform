import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'
import type { StrongSignal } from '../../types'

interface SignalPerformanceChartProps {
  signals: StrongSignal[]
  avgProfit: number
}

interface ChartEntry {
  symbol: string
  profit: number
  direction: 'long' | 'short'
  label: string
}

/**
 * Horizontal bar chart showing individual signal performance.
 * Book principles: horizontal bars for long labels, sorted by value,
 * color encodes direction (functional, not decorative),
 * direct labeling, no legend needed.
 */
export function SignalPerformanceChart({ signals, avgProfit }: SignalPerformanceChartProps) {
  const chartData = useMemo(() => {
    const calculated = signals
      .filter((s) => s.max_profit_pct != null)
      .map((s): ChartEntry => ({
        symbol: s.symbol.replace('USDT', ''),
        profit: s.max_profit_pct!,
        direction: s.direction,
        label: `${s.symbol.replace('USDT', '')} ${s.direction === 'long' ? '🧤' : '🎒'}`,
      }))
      .sort((a, b) => b.profit - a.profit)

    // Limit to top 12 signals for readability
    return calculated.slice(0, 12)
  }, [signals])

  if (chartData.length < 2) {
    return null
  }

  // Dynamic height based on signal count (28px per bar + margins)
  const chartHeight = Math.max(160, chartData.length * 28 + 40)

  return (
    <div className="card">
      <div className="card-header">Топ сигналов по профиту</div>
      <div className="px-1 pt-1" style={{ height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 4, right: 40, left: 4, bottom: 4 }}
          >
            <XAxis
              type="number"
              tick={{ fontSize: 9, fill: 'var(--tg-theme-hint-color, #999)' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `${v}%`}
            />
            <YAxis
              type="category"
              dataKey="label"
              tick={{ fontSize: 10, fill: 'var(--tg-theme-text-color, #000)' }}
              tickLine={false}
              axisLine={false}
              width={72}
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
              formatter={(value: number) => [`+${value.toFixed(2)}%`, 'Профит']}
            />
            {avgProfit > 0 && (
              <ReferenceLine
                x={avgProfit}
                stroke="var(--tg-theme-hint-color, #999)"
                strokeDasharray="4 4"
                strokeWidth={1}
                label={{
                  value: `Avg`,
                  position: 'top',
                  fontSize: 9,
                  fill: 'var(--tg-theme-hint-color, #999)',
                }}
              />
            )}
            <Bar dataKey="profit" radius={[0, 3, 3, 0]} maxBarSize={20}>
              {chartData.map((entry, index) => (
                <Cell
                  key={index}
                  fill={entry.direction === 'long' ? '#22c55e' : '#ef4444'}
                  opacity={0.8}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-4 text-xs text-tg-hint mt-1 pb-1">
        <span className="flex items-center gap-1">
          <span className="inline-block w-2.5 h-2.5 rounded-sm bg-long/80" />
          Long
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-2.5 h-2.5 rounded-sm bg-short/80" />
          Short
        </span>
      </div>
    </div>
  )
}

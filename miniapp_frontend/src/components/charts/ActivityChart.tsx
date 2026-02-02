import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import type { HourlyActivity } from '../../types'

interface ActivityChartProps {
  data: HourlyActivity[]
  median?: number
  color?: string
  height?: number
}

export function ActivityChart({
  data,
  median,
  color = '#2481cc',
  height = 200,
}: ActivityChartProps) {
  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--tg-theme-hint-color, #e0e0e0)"
            opacity={0.3}
          />
          <XAxis
            dataKey="hour"
            tick={{ fontSize: 10, fill: 'var(--tg-theme-hint-color, #999)' }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 10, fill: 'var(--tg-theme-hint-color, #999)' }}
            tickLine={false}
            axisLine={false}
            width={30}
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
          />
          {median !== undefined && median > 0 && (
            <ReferenceLine
              y={median}
              stroke="var(--tg-theme-hint-color, #999)"
              strokeDasharray="5 5"
              label={{
                value: `Медиана: ${median.toFixed(1)}`,
                position: 'right',
                fontSize: 10,
                fill: 'var(--tg-theme-hint-color, #999)',
              }}
            />
          )}
          <Line
            type="monotone"
            dataKey="count"
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: color }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

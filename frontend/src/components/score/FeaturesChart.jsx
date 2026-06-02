import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'

export function FeaturesChart({ features }) {
  if (!features || features.abnormal_return_day0 == null) {
    return (
      <div className="h-48 flex items-center justify-center bg-surface rounded-lg border border-border">
        <p className="text-xs text-secondary-foreground">No chart data available</p>
      </div>
    )
  }

  const data = [
    { name: 'Day 0', value: features.abnormal_return_day0 },
    { name: 'Day +1', value: features.abnormal_return_day1 },
    { name: 'Day +5', value: features.abnormal_return_day5 },
    { name: 'Day +30', value: features.abnormal_return_day30 },
  ]

  const arLabel = `Abnormal returns: Day 0 ${(features.abnormal_return_day0 * 100).toFixed(2)}%, Day +1 ${(features.abnormal_return_day1 * 100).toFixed(2)}%, Day +5 ${(features.abnormal_return_day5 * 100).toFixed(2)}%, Day +30 ${(features.abnormal_return_day30 * 100).toFixed(2)}%`

  return (
    <div className="h-48" role="img" aria-label={arLabel}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
          <XAxis
            dataKey="name"
            tick={{ fill: '#5a6a82', fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}
            axisLine={{ color: '#151d2e' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#5a6a82', fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}
            axisLine={{ color: '#151d2e' }}
            tickLine={false}
            tickFormatter={(v) => `${(v * 100).toFixed(1)}%`}
          />
          <Tooltip
            contentStyle={{
              background: '#0a0f1a',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              fontSize: '11px',
              fontFamily: 'JetBrains Mono, monospace',
              color: '#e8edf5',
              boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
            }}
            formatter={(value) => [
              `${value >= 0 ? '+' : ''}${(value * 100).toFixed(2)}% abnormal return`,
              'Abnormal Return',
            ]}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.value < 0 ? 'rgba(255,51,102,0.5)' : 'rgba(0,255,136,0.5)'}
                stroke={entry.value < 0 ? '#ff3366' : '#00ff88'}
                strokeWidth={1}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

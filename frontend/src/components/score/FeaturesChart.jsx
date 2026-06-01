import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'

export function FeaturesChart({ features, error }) {
  if (error) {
    return (
      <div
        className="h-48 flex flex-col items-center justify-center bg-surface rounded-lg border border-border"
        role="alert"
      >
        <svg className="w-8 h-8 text-muted-foreground mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-xs text-muted-foreground">{error}</p>
      </div>
    )
  }

  if (!features || features.abnormal_return_day0 == null) {
    return (
      <div className="h-48 flex items-center justify-center bg-surface rounded-lg border border-border">
        <p className="text-xs text-muted-foreground">No chart data available</p>
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
            tick={{ fill: '#4a5568', fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}
            axisLine={{ color: '#151d2e' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#4a5568', fontSize: 10, fontFamily: 'JetBrains Mono, monospace' }}
            axisLine={{ color: '#151d2e' }}
            tickLine={false}
            tickFormatter={(v) => `${(v * 100).toFixed(1)}%`}
          />
          <Tooltip
            contentStyle={{
              background: '#0f1520',
              border: '1px solid #1e293b',
              borderRadius: '8px',
              fontSize: '11px',
              fontFamily: 'JetBrains Mono, monospace',
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

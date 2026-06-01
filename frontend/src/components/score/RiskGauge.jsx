import { SEVERITY_COLORS } from '@/lib/utils'

export function RiskGauge({ score, prediction }) {
  const color = SEVERITY_COLORS[prediction] || '#4a5568'
  const circumference = 2 * Math.PI * 70
  const offset = circumference - (score / 100) * circumference

  return (
    <div
      className="relative w-48 h-48 mx-auto animate-in fade-in"
      role="img"
      aria-label={`Risk score: ${score} out of 100, severity: ${prediction}`}
    >
      <svg
        className="w-full h-full"
        style={{ transform: 'rotate(-90deg)' }}
        viewBox="0 0 160 160"
      >
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <circle
          cx="80"
          cy="80"
          r="70"
          fill="none"
          stroke="#151d2e"
          strokeWidth="8"
        />
        <circle
          cx="80"
          cy="80"
          r="70"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)',
            filter: 'url(#glow)',
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-4xl font-bold tracking-tight font-mono"
          style={{ color }}
        >
          {score}
        </span>
        <span className="text-[0.65rem] mt-1 tracking-widest uppercase text-muted-foreground">
          / 100
        </span>
      </div>
    </div>
  )
}

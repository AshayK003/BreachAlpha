import { useEffect, useState } from 'react'
import { SEVERITY_COLORS } from '@/lib/utils'

export function RiskGauge({ score, prediction }) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const color = SEVERITY_COLORS[prediction] || '#4a5568'
  const circumference = 2 * Math.PI * 70
  const offset = circumference - (animatedScore / 100) * circumference

  useEffect(() => {
    if (score === 0) {
      setAnimatedScore(0)
      return
    }
    const timeout = setTimeout(() => setAnimatedScore(score), 100)
    return () => clearTimeout(timeout)
  }, [score])

  return (
    <div
      className="relative w-48 h-48 mx-auto fade-in"
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
            transition: 'stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1)',
            filter: 'url(#glow)',
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-4xl font-bold tracking-tight font-mono"
          style={{ color, transition: 'color 0.3s ease' }}
          aria-live="polite"
        >
          {score}
        </span>
        <span className="text-[0.65rem] mt-1 tracking-widest uppercase text-dim">
          / 100
        </span>
      </div>
    </div>
  )
}

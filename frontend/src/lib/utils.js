import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatNumber(n) {
  if (n === null || n === undefined) return '—'
  if (typeof n === 'string') return n
  if (Math.abs(n) >= 1_000_000_000) return (n / 1_000_000_000).toFixed(1) + 'B'
  if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (Math.abs(n) >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return n.toFixed ? n.toFixed(n % 1 === 0 ? 0 : 2) : String(n)
}

export function formatPercent(n) {
  if (n === null || n === undefined) return '—'
  return (n * 100).toFixed(1) + '%'
}

export const SEVERITY_COLORS = {
  low: '#00ff88',
  medium: '#ff9500',
  high: '#ff6633',
  critical: '#ff3366',
}

export const SEVERITY_CLASSES = {
  low: 'severity-low',
  medium: 'severity-medium',
  high: 'severity-high',
  critical: 'severity-critical',
}

import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
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

import { Shield } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

export function Header() {
  return (
    <header className="mb-6 fade-in">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-cyan-700/10 border border-cyan-500/25 flex items-center justify-center shrink-0 glow-cyan">
          <Shield className="w-5 h-5 text-cyan" />
        </div>
        <div className="min-w-0">
          <h1 className="text-xl font-bold tracking-tight font-display text-primary" style={{ fontFamily: 'var(--font-display)' }}>
            BreachAlpha
          </h1>
          <p className="text-xs text-dim mt-0.5 font-mono tracking-wide">
            Cyber Risk Quantification Terminal
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Badge variant="outline" className="terminal-label border-cyan-500/20 text-cyan bg-cyan/5 shrink-0">
            v0.2.0
          </Badge>
          <div className="status-dot pulse w-2 h-2 rounded-full bg-green shrink-0" />
        </div>
      </div>
    </header>
  )
}

import { cn } from '@/lib/utils'

export function Header({ health }) {
  const statusColor = health?.status === 'ok'
    ? 'bg-emerald-400'
    : health?.status === 'degraded'
      ? 'bg-amber-400'
      : 'bg-slate-500'

  const pulseClass = health?.status === 'ok' ? 'animate-pulse' : ''

  return (
    <header
      className="sticky top-0 z-50 border-b border-border bg-background/85 backdrop-blur-xl"
      role="banner"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, rgba(0, 240, 255, 0.15) 0%, rgba(0, 100, 200, 0.1) 100%)',
              border: '1px solid rgba(0, 240, 255, 0.3)',
            }}
          >
            <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight font-mono text-foreground">
              BreachAlpha
            </h1>
            <p className="text-[0.6rem] tracking-widest uppercase -mt-0.5 text-cyan-600">
              Cyber-Financial Risk Quantifier
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2.5" role="status">
          <div className={cn('status-dot w-2 h-2 rounded-full', statusColor, pulseClass)} />
          <span className="text-[0.6875rem] text-muted-foreground">
            {health?.model_loaded ? 'Model Ready' : 'No Model'}
          </span>
        </div>
      </div>
    </header>
  )
}

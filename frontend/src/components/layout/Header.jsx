import { Badge } from '@/components/ui/badge'

export function Header({ health }) {
  return (
    <header className="mb-6 fade-in">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-cyan-700/10 border border-cyan-500/25 flex items-center justify-center shrink-0 glow-cyan">
          <svg className="w-5 h-5 text-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div className="min-w-0 flex-1">
          <h1 className="text-xl font-bold tracking-tight font-display text-primary leading-tight" style={{ fontFamily: 'var(--font-display)' }}>
            BreachAlpha
          </h1>
          <p className="text-[0.65rem] text-dim font-mono tracking-wider uppercase">
            Cyber Risk Quantification Terminal
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Badge variant="outline" className="terminal-label border-cyan-500/20 text-cyan bg-cyan/5">
            v0.2.0
          </Badge>
          <div
            className={`status-dot w-2 h-2 rounded-full ${health?.status === 'ok' ? 'bg-green pulse' : 'bg-red'}`}
            title={health?.status === 'ok' ? 'Backend connected' : 'Backend offline'}
          />
          <a
            href="https://github.com/AshayK003/BreachAlpha"
            target="_blank"
            rel="noopener noreferrer"
            className="ml-1 p-1.5 rounded-lg text-dim hover:text-cyan hover:bg-cyan/5 transition-all duration-200"
            title="View on GitHub"
            aria-label="View source code on GitHub"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  )
}

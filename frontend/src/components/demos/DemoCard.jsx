import { cn, SEVERITY_COLORS, SEVERITY_CLASSES } from '@/lib/utils'

export function DemoCard({ demo, onClick, onExplain }) {
  return (
    <button
      onClick={() => onClick(demo)}
      className="terminal-card corner-accent p-4 text-left w-full hover-lift"
    >
      <div className="flex items-start justify-between mb-2.5">
        <div className="min-w-0">
          <h3 className="font-semibold text-sm truncate font-mono text-foreground">
            {demo.company}
          </h3>
          <span className="text-[0.65rem] tracking-wider uppercase text-secondary-foreground">
            {demo.ticker}
          </span>
        </div>
        {demo.risk_score && (
          <span
            className={cn(
              'text-[0.65rem] px-1.5 py-0.5 rounded-full font-mono shrink-0 ml-2',
              demo.prediction && SEVERITY_CLASSES[demo.prediction]
                ? SEVERITY_CLASSES[demo.prediction]
                : 'bg-surface text-secondary-foreground border border-border'
            )}
          >
            {demo.prediction?.toUpperCase()}
          </span>
        )}
      </div>
      <p className="text-xs mb-3 line-clamp-2 text-secondary-foreground">{demo.description}</p>
      <div className="flex items-center justify-between text-[0.6875rem]">
        <span className="text-secondary-foreground">{demo.breach_date}</span>
        <span className="text-secondary-foreground">
          {(demo.pwn_count / 1_000_000).toFixed(0)}M records
        </span>
      </div>
      {demo.risk_score && (
        <div className="mt-2.5 pt-2.5 flex items-center justify-between border-t border-border">
          <span className="text-[0.65rem] tracking-wider uppercase text-dim">
            Risk Score
          </span>
          <div className="flex items-center gap-2.5">
            <span
              className="text-lg font-bold font-mono"
              style={{ color: SEVERITY_COLORS[demo.prediction] }}
            >
              {demo.risk_score}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation()
                onExplain(demo.ticker || demo.company)
              }}
              className="text-[0.6875rem] hover:opacity-80 transition-opacity text-cyan"
              title="Explain this score"
            >
              Explain
            </button>
          </div>
        </div>
      )}
    </button>
  )
}

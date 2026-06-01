import { cn, SEVERITY_COLORS, SEVERITY_CLASSES } from '@/lib/utils'

export function DemoCard({ demo, onClick, onExplain }) {
  return (
    <button
      onClick={() => onClick(demo)}
      onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.98)')}
      onMouseUp={(e) => (e.currentTarget.style.transform = '')}
      onMouseLeave={(e) => (e.currentTarget.style.transform = '')}
      className="card-hover card corner-accent p-4 text-left w-full bg-card border border-border rounded-lg transition-transform"
      style={{ transition: 'transform 0.15s cubic-bezier(0.4, 0, 0.2, 1)' }}
    >
      <div className="flex items-start justify-between mb-2.5">
        <div className="min-w-0">
          <h3 className="font-semibold text-sm truncate font-mono text-foreground">
            {demo.company}
          </h3>
          <span className="text-[0.65rem] tracking-wider uppercase text-muted-foreground">
            {demo.ticker}
          </span>
        </div>
        {demo.risk_score && (
          <span
            className={cn(
              'text-[0.65rem] px-1.5 py-0.5 rounded-full font-mono shrink-0 ml-2',
              demo.prediction && SEVERITY_CLASSES[demo.prediction]
                ? SEVERITY_CLASSES[demo.prediction]
                : 'bg-surface text-muted-foreground border border-border'
            )}
          >
            {demo.prediction?.toUpperCase()}
          </span>
        )}
      </div>
      <p className="text-xs mb-3 line-clamp-2 text-muted-foreground">{demo.description}</p>
      <div className="flex items-center justify-between text-[0.6875rem]">
        <span className="text-muted-foreground">{demo.breach_date}</span>
        <span className="text-muted-foreground">
          {(demo.pwn_count / 1_000_000).toFixed(0)}M records
        </span>
      </div>
      {demo.risk_score && (
        <div
          className="mt-2.5 pt-2.5 flex items-center justify-between"
          style={{ borderTop: '1px solid var(--border)' }}
        >
          <span className="text-[0.65rem] tracking-wider uppercase text-muted-foreground">
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
              className="text-[0.6875rem] hover:opacity-80 transition-opacity text-cyan-400"
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

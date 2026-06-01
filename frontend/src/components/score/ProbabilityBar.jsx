export function ProbabilityBar({ label, probability, color }) {
  return (
    <div
      className="flex items-center gap-3"
      role="group"
      aria-label={`${label}: ${(probability * 100).toFixed(1)}%`}
    >
      <span className="w-20 text-[0.6875rem] capitalize tracking-wide text-muted-foreground">
        {label}
      </span>
      <div
        className="flex-1 h-2 rounded-full overflow-hidden bg-border"
        role="meter"
        aria-valuenow={Math.round(probability * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${probability * 100}%`,
            backgroundColor: color,
            boxShadow: `0 0 8px ${color}40`,
          }}
        />
      </div>
      <span className="w-14 text-[0.6875rem] text-right font-mono text-muted-foreground">
        {(probability * 100).toFixed(1)}%
      </span>
    </div>
  )
}

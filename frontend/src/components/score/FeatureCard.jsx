export function FeatureCard({ label, value, unit, negative }) {
  const color = negative ? 'text-red-400' : 'text-foreground'

  return (
    <div
      className="corner-accent p-3 bg-card border border-border rounded-lg"
    >
      <div className="text-[0.625rem] tracking-wider uppercase mb-0.5 text-muted-foreground">
        {label}
      </div>
      <div className={`text-sm font-semibold font-mono ${color}`}>
        {typeof value === 'number' ? value.toFixed(4) : value || 'N/A'}
        {unit && (
          <span className="text-[0.65rem] ml-0.5 font-normal text-muted-foreground">
            {unit}
          </span>
        )}
      </div>
    </div>
  )
}

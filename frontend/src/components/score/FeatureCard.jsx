export function FeatureCard({ label, value, unit, negative }) {
  const color = negative ? 'text-red-400' : 'text-primary'

  return (
    <div className="corner-accent p-3 bg-card border border-border rounded-lg hover:border-border-bright transition-all duration-300 ease-out hover:-translate-y-0.5">
      <div className="text-[0.625rem] tracking-wider uppercase mb-0.5 text-dim">
        {label}
      </div>
      <div className={`text-sm font-semibold font-mono ${color} transition-colors duration-200`}>
        {typeof value === 'number' ? value.toFixed(4) : value || 'N/A'}
        {unit && (
          <span className="text-[0.65rem] ml-0.5 font-normal text-dim">
            {unit}
          </span>
        )}
      </div>
    </div>
  )
}

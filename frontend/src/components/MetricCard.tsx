interface MetricCardProps {
  label: string
  value: string | number
  sub?: string
  tone?: 'default' | 'bull' | 'bear' | 'warn' | 'accent'
}

export function MetricCard({ label, value, sub, tone = 'default' }: MetricCardProps) {
  return (
    <div className={`metric-card metric-${tone}`}>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      {sub && <span className="metric-sub">{sub}</span>}
    </div>
  )
}

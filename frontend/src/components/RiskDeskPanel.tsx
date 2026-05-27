import type { RiskDeskResponse } from '../api/types'

interface RiskDeskPanelProps {
  risk: RiskDeskResponse | null
}

export function RiskDeskPanel({ risk }: RiskDeskPanelProps) {
  if (!risk) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Risk Desk</h2></div>
        <div className="loading-block">Loading risk…</div>
      </section>
    )
  }

  return (
    <section className="panel risk-panel">
      <div className="panel-head">
        <h2>Portfolio Risk</h2>
        {risk.high_priority_sessions_active && (
          <span className="panel-tag tag-ok">High-priority session</span>
        )}
      </div>

      <div className="risk-grid">
        <div className="risk-stat">
          <span>Bullish</span>
          <strong className="text-ok">{risk.bullish}</strong>
        </div>
        <div className="risk-stat">
          <span>Bearish</span>
          <strong className="text-bad">{risk.bearish}</strong>
        </div>
        <div className="risk-stat">
          <span>Stand Aside</span>
          <strong>{risk.stand_aside}</strong>
        </div>
        <div className="risk-stat">
          <span>Entropy Blocked</span>
          <strong className="text-bad">{risk.entropy_blocked}</strong>
        </div>
        <div className="risk-stat">
          <span>Circuit Breakers</span>
          <strong className="text-warn">{risk.circuit_breakers}</strong>
        </div>
        <div className="risk-stat">
          <span>Avg Entropy</span>
          <strong>{risk.avg_entropy.toFixed(3)}</strong>
        </div>
        <div className="risk-stat">
          <span>Avg Size</span>
          <strong>{Math.round(risk.avg_position_multiplier * 100)}%</strong>
        </div>
        <div className="risk-stat">
          <span>At Risk</span>
          <strong className="text-bad">{risk.pairs_at_risk.length}</strong>
        </div>
      </div>

      {risk.pairs_at_risk.length > 0 && (
        <div className="risk-list">
          <span>Pairs at risk:</span>
          <div className="risk-tags">
            {risk.pairs_at_risk.map((s) => (
              <span key={s} className="risk-tag">{s}</span>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

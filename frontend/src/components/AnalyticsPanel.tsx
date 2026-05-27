import type { AnalyticsResponse } from '../api/types'

interface AnalyticsPanelProps {
  analytics: AnalyticsResponse | null
  loading: boolean
}

function WeightBar({ label, weight }: { label: string; weight: number }) {
  return (
    <div className="weight-row">
      <span>{label}</span>
      <div className="weight-track">
        <div className="weight-fill" style={{ width: `${weight * 100}%` }} />
      </div>
      <span className="mono">{Math.round(weight * 100)}%</span>
    </div>
  )
}

export function AnalyticsPanel({ analytics, loading }: AnalyticsPanelProps) {
  if (loading && !analytics) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Engine Analytics</h2></div>
        <div className="loading-block">Loading analytics…</div>
      </section>
    )
  }

  if (!analytics) return null

  const { garch, mp_filter, pivot_weights } = analytics

  return (
    <section className="panel analytics-panel">
      <div className="panel-head">
        <h2>Engine Analytics</h2>
        <span className="panel-tag">{analytics.atr_regime}</span>
      </div>

      <div className="analytics-grid">
        <div className="analytics-block">
          <h3>GARCH Volatility Overlay</h3>
          <dl className="kv-list">
            <div><dt>Regime</dt><dd>{garch.regime}</dd></div>
            <div><dt>Percentile</dt><dd>{garch.percentile.toFixed(1)}th</dd></div>
            <div><dt>Cond. Variance</dt><dd className="mono">{garch.conditional_variance.toExponential(2)}</dd></div>
            <div><dt>Size Multiplier</dt><dd>{Math.round(garch.position_size_multiplier * 100)}%</dd></div>
            <div><dt>Circuit Breaker</dt><dd className={garch.circuit_breaker_active ? 'text-bad' : 'text-ok'}>
              {garch.circuit_breaker_active ? 'ACTIVE' : 'Off'}
            </dd></div>
            <div><dt>Block Breakouts</dt><dd>{garch.block_breakout_entries ? 'Yes' : 'No'}</dd></div>
          </dl>
        </div>

        <div className="analytics-block">
          <h3>Marchenko-Pastur Filter</h3>
          <dl className="kv-list">
            <div><dt>Signals Retained</dt><dd>{mp_filter.signals_retained} / {mp_filter.max_lags}</dd></div>
            <div><dt>Noise Ceiling λ+</dt><dd className="mono">{mp_filter.noise_ceiling.toFixed(6)}</dd></div>
            <div><dt>γ (aspect ratio)</dt><dd>{mp_filter.gamma}</dd></div>
            <div><dt>ATR</dt><dd className="mono">{analytics.atr.toFixed(5)}</dd></div>
            <div><dt>ATR Percentile</dt><dd>{analytics.atr_percentile.toFixed(1)}th</dd></div>
          </dl>
        </div>

        <div className="analytics-block full-width">
          <h3>Dynamic Pivot Weights</h3>
          <WeightBar label="Standard" weight={pivot_weights.standard} />
          <WeightBar label="Camarilla" weight={pivot_weights.camarilla} />
          <WeightBar label="Fibonacci" weight={pivot_weights.fibonacci} />
          <WeightBar label="Volume Profile" weight={pivot_weights.volume_profile} />
        </div>
      </div>
    </section>
  )
}

import type { AnalyticsResponse, ForecastResponse } from '../api/types'
import { MetricCard } from './MetricCard'
import { ScenarioBadge } from './ScenarioBadge'

interface ForecastPanelProps {
  forecast: ForecastResponse | null
  analytics: AnalyticsResponse | null
  loading: boolean
}

function fmt(price: number | null | undefined, symbol: string) {
  if (price == null) return '—'
  const digits = symbol.includes('JPY') ? 3 : 5
  return price.toFixed(digits)
}

export function ForecastPanel({ forecast, analytics, loading }: ForecastPanelProps) {
  if (loading && !forecast) {
    return (
      <section className="panel forecast-panel">
        <div className="panel-head"><h2>Execution Forecast</h2></div>
        <div className="loading-block">Loading forecast…</div>
      </section>
    )
  }

  if (!forecast) {
    return (
      <section className="panel forecast-panel">
        <div className="panel-head"><h2>Execution Forecast</h2></div>
        <div className="loading-block">No forecast available</div>
      </section>
    )
  }

  const ts = new Date(forecast.timestamp_wat).toLocaleString('en-GB', {
    timeZone: 'Africa/Lagos',
    dateStyle: 'medium',
    timeStyle: 'short',
  })

  return (
    <section className="panel forecast-panel">
      <div className="panel-head">
        <div>
          <h2>Execution Forecast</h2>
          <p className="panel-sub">
            Basilica scenario · {ts} WAT
            {analytics && (
              <> · Last {fmt(analytics.price, forecast.symbol)} ({analytics.change_pct >= 0 ? '+' : ''}{analytics.change_pct.toFixed(3)}%)</>
            )}
          </p>
        </div>
        <ScenarioBadge scenario={forecast.scenario} />
      </div>

      <div className="metric-grid">
        <MetricCard
          label="Entry Low"
          value={fmt(forecast.entry_range?.low, forecast.symbol)}
          tone="bull"
        />
        <MetricCard
          label="Entry High"
          value={fmt(forecast.entry_range?.high, forecast.symbol)}
          tone="bull"
        />
        <MetricCard label="Take Profit (POC)" value={fmt(forecast.tp, forecast.symbol)} tone="accent" />
        <MetricCard label="Stop Loss" value={fmt(forecast.sl, forecast.symbol)} tone="bear" />
      </div>

      <div className="forecast-meta">
        <div className="meta-row">
          <span>Regime</span>
          <strong>{forecast.regime}</strong>
        </div>
        <div className="meta-row">
          <span>MP Signals Retained</span>
          <strong>{forecast.mp_signals_retained}</strong>
        </div>
        <div className="meta-row">
          <span>Position Size</span>
          <strong>{Math.round(forecast.position_size_multiplier * 100)}%</strong>
        </div>
        <div className="meta-row">
          <span>Entropy Clearance</span>
          <strong className={forecast.entropy.clearance ? 'text-ok' : 'text-bad'}>
            {forecast.entropy.clearance ? 'Cleared' : 'Blocked'}
          </strong>
        </div>
      </div>
    </section>
  )
}

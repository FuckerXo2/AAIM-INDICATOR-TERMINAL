import type { HealthResponse, PairInfo } from '../api/types'

interface HealthPanelProps {
  health: HealthResponse | null
  pairs: PairInfo[]
  selected: string
}

function statusClass(status: string) {
  if (status === 'live' || status === 'bootstrap' || status === 'ok') return 'ok'
  if (status === 'pending' || status === 'fallback') return 'warn'
  return 'bad'
}

export function HealthPanel({ health, pairs, selected }: HealthPanelProps) {
  const pair = pairs.find((p) => p.symbol === selected)
  const scraper = health?.scrapers.find((s) => s.symbol === selected)

  return (
    <section className="panel health-panel">
      <div className="panel-head">
        <h2>Desk Workflow</h2>
        <span className={`panel-tag tag-${health?.status ?? 'warn'}`}>
          {health?.status ?? 'offline'}
        </span>
      </div>

      {pair && (
        <dl className="info-list">
          <div><dt>ECN Venue</dt><dd>{pair.ecn_venue}</dd></div>
          <div><dt>CME Proxy</dt><dd>{pair.cme_futures_proxy}</dd></div>
          <div><dt>Macro Anchor</dt><dd>{pair.macro_anchor}</dd></div>
        </dl>
      )}

      {scraper && (
        <div className="scraper-grid">
          <div className="scraper-item">
            <span>OHLCV</span>
            <strong className={`text-${statusClass(scraper.ohlcv)}`}>{scraper.ohlcv}</strong>
            {scraper.last_bar_age_seconds != null && (
              <small>{scraper.last_bar_age_seconds.toFixed(0)}s ago</small>
            )}
          </div>
          <div className="scraper-item">
            <span>Futures</span>
            <strong className={`text-${statusClass(scraper.futures)}`}>{scraper.futures}</strong>
          </div>
          <div className="scraper-item">
            <span>Yields</span>
            <strong className={`text-${statusClass(scraper.yield_scraper)}`}>{scraper.yield_scraper}</strong>
          </div>
        </div>
      )}

      <ol className="workflow-steps">
        <li>Health check — verify scrapers live, bar age &lt; 90s</li>
        <li>Entropy gate — reject HIGH_RISK outright</li>
        <li>Regime check — apply 50% haircut in High-Entropy Shock</li>
        <li>Forecast pull — cross-check entry vs VAH/VAL</li>
        <li>Session windows — 08:00 & 13:00 WAT priority</li>
      </ol>
    </section>
  )
}

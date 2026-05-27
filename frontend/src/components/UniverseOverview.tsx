import type { DeskOverviewResponse } from '../api/types'
import { ScenarioBadge } from './ScenarioBadge'

interface UniverseOverviewProps {
  overview: DeskOverviewResponse | null
  selected: string
  onSelect: (symbol: string) => void
  loading: boolean
}

function fmtPrice(price: number, symbol: string) {
  return price.toFixed(symbol.includes('JPY') ? 3 : 5)
}

export function UniverseOverview({ overview, selected, onSelect, loading }: UniverseOverviewProps) {
  if (loading && !overview) {
    return (
      <section className="panel universe-panel">
        <div className="panel-head"><h2>Universe Overview</h2></div>
        <div className="loading-block">Loading universe…</div>
      </section>
    )
  }

  if (!overview) return null

  return (
    <section className="panel universe-panel">
      <div className="panel-head">
        <div>
          <h2>Universe Overview</h2>
          <p className="panel-sub">
            {overview.actionable_count} actionable · {overview.blocked_count} entropy blocked · {overview.circuit_breaker_count} circuit breakers
          </p>
        </div>
      </div>

      <div className="universe-cards">
        {overview.pairs.map((row) => (
          <button
            type="button"
            key={row.symbol}
            className={`universe-card ${row.symbol === selected ? 'selected' : ''} ${row.actionable ? 'actionable' : ''}`}
            onClick={() => onSelect(row.symbol)}
          >
            <div className="universe-card-top">
              <div>
                <strong className="mono">{row.symbol}</strong>
                <small>{row.asset_class}</small>
              </div>
              <ScenarioBadge scenario={row.scenario} />
            </div>
            <div className="universe-card-metrics">
              <div>
                <span>Price</span>
                <strong className="mono">{fmtPrice(row.price, row.symbol)}</strong>
              </div>
              <div>
                <span>Chg</span>
                <strong className={row.change_pct >= 0 ? 'text-ok' : 'text-bad'}>
                  {row.change_pct >= 0 ? '+' : ''}{row.change_pct.toFixed(3)}%
                </strong>
              </div>
              <div>
                <span>Entropy</span>
                <strong className={row.clearance ? 'text-ok' : 'text-bad'}>{row.entropy_bits.toFixed(2)}</strong>
              </div>
              <div>
                <span>Size</span>
                <strong>{Math.round(row.position_size_multiplier * 100)}%</strong>
              </div>
            </div>
            <div className="universe-card-footer">
              <span>{row.regime} · {row.garch_regime}</span>
              {row.actionable ? (
                <span className="status-pill pill-ok">Go</span>
              ) : row.clearance ? (
                <span className="status-pill pill-warn">Wait</span>
              ) : (
                <span className="status-pill pill-bad">Block</span>
              )}
            </div>
          </button>
        ))}
      </div>

      <div className="table-wrap universe-table-wrap">
        <table className="universe-table">
          <thead>
            <tr>
              <th>Pair</th>
              <th>Price</th>
              <th>Chg%</th>
              <th>Scenario</th>
              <th>Regime</th>
              <th>GARCH</th>
              <th>Entropy</th>
              <th>Size</th>
              <th>MP</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {overview.pairs.map((row) => (
              <tr
                key={row.symbol}
                className={`${row.symbol === selected ? 'selected' : ''} ${row.actionable ? 'actionable' : ''}`}
                onClick={() => onSelect(row.symbol)}
              >
                <td>
                  <strong>{row.symbol}</strong>
                  <small>{row.asset_class}</small>
                </td>
                <td className="mono">{fmtPrice(row.price, row.symbol)}</td>
                <td className={row.change_pct >= 0 ? 'text-ok' : 'text-bad'}>
                  {row.change_pct >= 0 ? '+' : ''}{row.change_pct.toFixed(3)}%
                </td>
                <td><ScenarioBadge scenario={row.scenario} /></td>
                <td>{row.regime}</td>
                <td>{row.garch_regime}</td>
                <td className={row.clearance ? 'text-ok' : 'text-bad'}>{row.entropy_bits.toFixed(2)}</td>
                <td>{Math.round(row.position_size_multiplier * 100)}%</td>
                <td>{row.mp_signals}</td>
                <td>
                  {row.actionable ? (
                    <span className="status-pill pill-ok">Go</span>
                  ) : row.clearance ? (
                    <span className="status-pill pill-warn">Wait</span>
                  ) : (
                    <span className="status-pill pill-bad">Block</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

import type { CotResponse } from '../api/types'

interface CotPanelProps {
  cot: CotResponse | null
}

export function CotPanel({ cot }: CotPanelProps) {
  if (!cot || cot.positions.length === 0) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>CFTC Positioning</h2></div>
        <div className="loading-block">Loading COT data…</div>
      </section>
    )
  }

  return (
    <section className="panel cot-panel">
      <div className="panel-head">
        <h2>CFTC Leveraged Funds</h2>
        <span className="panel-tag">Weekly COT</span>
      </div>

      <table className="cot-table">
        <thead>
          <tr>
            <th>CCY</th>
            <th>Net Long</th>
            <th>Net Short</th>
            <th>Net</th>
            <th>Bias</th>
          </tr>
        </thead>
        <tbody>
          {cot.positions.map((p) => (
            <tr key={p.currency}>
              <td><strong>{p.currency}</strong></td>
              <td className="mono">{p.net_long.toLocaleString()}</td>
              <td className="mono">{p.net_short.toLocaleString()}</td>
              <td className={`mono ${p.net_position >= 0 ? 'text-ok' : 'text-bad'}`}>
                {p.net_position >= 0 ? '+' : ''}{p.net_position.toLocaleString()}
              </td>
              <td>
                <span className={`bias-pill ${p.net_position >= 0 ? 'bull' : 'bear'}`}>{p.bias}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

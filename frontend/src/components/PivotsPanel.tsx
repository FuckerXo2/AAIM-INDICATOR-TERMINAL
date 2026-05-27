import type { PivotLevels, PivotsResponse } from '../api/types'
import { useState } from 'react'

interface PivotsPanelProps {
  pivots: PivotsResponse | null
  symbol: string
  loading: boolean
}

type Family = 'standard' | 'camarilla' | 'fibonacci'

const FAMILIES: { id: Family; label: string }[] = [
  { id: 'standard', label: 'Standard' },
  { id: 'camarilla', label: 'Camarilla' },
  { id: 'fibonacci', label: 'Fibonacci' },
]

function fmt(price: number | null | undefined, symbol: string) {
  if (price == null) return '—'
  return price.toFixed(symbol.includes('JPY') ? 3 : 5)
}

function levelRows(levels: PivotLevels) {
  const order = ['R4', 'R3', 'R2', 'R1', 'P', 'S1', 'S2', 'S3', 'S4'] as const
  return order
    .filter((k) => levels[k] != null)
    .map((k) => ({ key: k, value: levels[k] as number, kind: k.startsWith('R') ? 'r' : k.startsWith('S') ? 's' : 'p' }))
}

export function PivotsPanel({ pivots, symbol, loading }: PivotsPanelProps) {
  const [family, setFamily] = useState<Family>('camarilla')

  if (loading && !pivots) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Pivot Levels</h2></div>
        <div className="loading-block">Loading pivots…</div>
      </section>
    )
  }

  if (!pivots) return null

  const rows = levelRows(pivots[family])

  return (
    <section className="panel pivots-panel">
      <div className="panel-head">
        <h2>Pivot Levels</h2>
        <span className="panel-tag">NY Close anchor</span>
      </div>

      <div className="tab-row">
        {FAMILIES.map((f) => (
          <button
            key={f.id}
            type="button"
            className={`tab-btn ${family === f.id ? 'active' : ''}`}
            onClick={() => setFamily(f.id)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <table className="pivot-table">
        <thead>
          <tr>
            <th>Level</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key} className={`pivot-${row.kind}`}>
              <td>{row.key}</td>
              <td>{fmt(row.value, symbol)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

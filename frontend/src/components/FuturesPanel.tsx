import type { FuturesResponse } from '../api/types'

interface FuturesPanelProps {
  futures: FuturesResponse | null
}

function fmt(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toFixed(0)
}

export function FuturesPanel({ futures }: FuturesPanelProps) {
  if (!futures) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>CME Futures Proxy</h2></div>
        <div className="loading-block">Loading futures…</div>
      </section>
    )
  }

  return (
    <section className="panel futures-panel">
      <div className="panel-head">
        <div>
          <h2>CME Futures Proxy</h2>
          <p className="panel-sub">{futures.cme_proxy}</p>
        </div>
        <span className="panel-tag">{futures.source}</span>
      </div>

      <div className="futures-stats">
        <div className="futures-stat">
          <span>Volume</span>
          <strong className="mono">{fmt(futures.volume)}</strong>
        </div>
        <div className="futures-stat">
          <span>Open Interest</span>
          <strong className="mono">{fmt(futures.open_interest)}</strong>
        </div>
      </div>
    </section>
  )
}

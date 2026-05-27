import type { VolumeProfile } from '../api/types'

interface VolumeProfilePanelProps {
  profile: VolumeProfile | null
  symbol: string
  loading: boolean
}

function fmt(price: number, symbol: string) {
  return price.toFixed(symbol.includes('JPY') ? 3 : 5)
}

export function VolumeProfilePanel({ profile, symbol, loading }: VolumeProfilePanelProps) {
  if (loading && !profile) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Volume Profile</h2></div>
        <div className="loading-block">Loading profile…</div>
      </section>
    )
  }

  if (!profile) return null

  const levels = [
    { key: 'VAH', value: profile.VAH, tone: 'resistance' },
    { key: 'POC', value: profile.POC, tone: 'poc' },
    { key: 'VAL', value: profile.VAL, tone: 'support' },
    { key: 'LVN', value: profile.LVN, tone: 'lvn' },
  ]

  const min = Math.min(...levels.map((l) => l.value))
  const max = Math.max(...levels.map((l) => l.value))
  const span = max - min || 1

  return (
    <section className="panel volume-panel">
      <div className="panel-head">
        <h2>Volume Profile</h2>
        <span className="panel-tag">70% Value Area</span>
      </div>

      <div className="volume-chart">
        {levels.map((level) => {
          const pct = ((level.value - min) / span) * 100
          return (
            <div key={level.key} className="volume-row">
              <span className="volume-key">{level.key}</span>
              <div className="volume-track">
                <div
                  className={`volume-bar bar-${level.tone}`}
                  style={{ width: `${Math.max(pct, 8)}%` }}
                />
              </div>
              <span className="volume-price">{fmt(level.value, symbol)}</span>
            </div>
          )
        })}
      </div>

      <p className="volume-note">
        POC is the primary gravitational magnet. VAH/VAL define the balanced auction range; LVN marks breakout acceleration zones.
      </p>
    </section>
  )
}

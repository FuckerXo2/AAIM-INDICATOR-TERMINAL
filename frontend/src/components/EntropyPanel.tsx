import type { EntropyResponse } from '../api/types'

interface EntropyPanelProps {
  entropy: EntropyResponse | null
  loading: boolean
}

function tone(classification: string) {
  if (classification.startsWith('LOW_RISK')) return 'ok'
  if (classification.startsWith('MODERATE')) return 'warn'
  return 'bad'
}

function label(classification: string) {
  return classification.replace(/_/g, ' ')
}

export function EntropyPanel({ entropy, loading }: EntropyPanelProps) {
  if (loading && !entropy) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Entropy Sentinel</h2></div>
        <div className="loading-block">Loading entropy…</div>
      </section>
    )
  }

  if (!entropy) return null

  const t = tone(entropy.classification)
  const pct = Math.min((entropy.entropy_bits / 1.585) * 100, 100)

  return (
    <section className="panel entropy-panel">
      <div className="panel-head">
        <h2>Entropy Sentinel</h2>
        <span className={`clearance-badge clearance-${t}`}>
          {entropy.clearance ? 'Clearance OK' : 'Blocked'}
        </span>
      </div>

      <div className="entropy-meter">
        <div className="entropy-value">{entropy.entropy_bits.toFixed(3)} bits</div>
        <div className="entropy-track">
          <div className={`entropy-fill fill-${t}`} style={{ width: `${pct}%` }} />
        </div>
        <div className="entropy-thresholds">
          <span>0.40 Low</span>
          <span>0.85 High</span>
        </div>
      </div>

      <p className={`entropy-class class-${t}`}>{label(entropy.classification)}</p>
    </section>
  )
}

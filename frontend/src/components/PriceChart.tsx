import type { BarsResponse, VolumeProfile } from '../api/types'

interface PriceChartProps {
  bars: BarsResponse | null
  profile: VolumeProfile | null
  symbol: string
  entryLow?: number | null
  entryHigh?: number | null
  tp?: number | null
  sl?: number | null
}

export function PriceChart({ bars, profile, symbol, entryLow, entryHigh, tp, sl }: PriceChartProps) {
  if (!bars || bars.bars.length < 5) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Price Chart</h2></div>
        <div className="loading-block">Loading bars…</div>
      </section>
    )
  }

  const data = bars.bars
  const W = 720
  const H = 220
  const pad = { t: 12, r: 12, b: 24, l: 56 }
  const iw = W - pad.l - pad.r
  const ih = H - pad.t - pad.b

  const highs = data.map((b) => b.high)
  const lows = data.map((b) => b.low)
  let yMin = Math.min(...lows)
  let yMax = Math.max(...highs)

  const levels = [profile?.VAH, profile?.POC, profile?.VAL, profile?.LVN, entryLow, entryHigh, tp, sl].filter(
    (v): v is number => v != null,
  )
  if (levels.length) {
    yMin = Math.min(yMin, ...levels)
    yMax = Math.max(yMax, ...levels)
  }
  const yPad = (yMax - yMin) * 0.08 || 0.001
  yMin -= yPad
  yMax += yPad

  const xScale = (i: number) => pad.l + (i / (data.length - 1)) * iw
  const yScale = (v: number) => pad.t + ih - ((v - yMin) / (yMax - yMin)) * ih

  const candleW = Math.max(2, iw / data.length - 1)

  const levelLine = (price: number, color: string, label: string, dash?: string) => (
    <g key={label}>
      <line
        x1={pad.l}
        x2={W - pad.r}
        y1={yScale(price)}
        y2={yScale(price)}
        stroke={color}
        strokeWidth={1}
        strokeDasharray={dash}
        opacity={0.8}
      />
      <text x={W - pad.r + 4} y={yScale(price) + 3} fill={color} fontSize={9}>{label}</text>
    </g>
  )

  return (
    <section className="panel chart-panel">
      <div className="panel-head">
        <h2>15m Price Chart</h2>
        <span className="panel-tag">{data.length} bars</span>
      </div>

      <svg viewBox={`0 0 ${W + 40} ${H}`} className="price-chart">
        {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
          const v = yMin + (yMax - yMin) * (1 - pct)
          const y = pad.t + ih * pct
          return (
            <g key={pct}>
              <line x1={pad.l} x2={W - pad.r} y1={y} y2={y} stroke="#1e2a38" strokeWidth={1} />
              <text x={pad.l - 6} y={y + 3} fill="#7d8fa3" fontSize={9} textAnchor="end">
                {v.toFixed(symbol.includes('JPY') ? 3 : 5)}
              </text>
            </g>
          )
        })}

        {profile && levelLine(profile.VAH, '#f87171', 'VAH', '4 3')}
        {profile && levelLine(profile.POC, '#3b82f6', 'POC')}
        {profile && levelLine(profile.VAL, '#22c55e', 'VAL', '4 3')}
        {profile && levelLine(profile.LVN, '#f59e0b', 'LVN', '2 2')}
        {entryLow != null && levelLine(entryLow, '#22c55e', 'Entry', '3 3')}
        {entryHigh != null && entryHigh !== entryLow && levelLine(entryHigh, '#22c55e', '', '3 3')}
        {tp != null && levelLine(tp, '#6366f1', 'TP')}
        {sl != null && levelLine(sl, '#ef4444', 'SL')}

        {data.map((bar, i) => {
          const bull = bar.close >= bar.open
          const color = bull ? '#22c55e' : '#ef4444'
          const cx = xScale(i)
          const yHigh = yScale(bar.high)
          const yLow = yScale(bar.low)
          const yOpen = yScale(bar.open)
          const yClose = yScale(bar.close)
          const bodyTop = Math.min(yOpen, yClose)
          const bodyH = Math.max(Math.abs(yClose - yOpen), 1)
          return (
            <g key={i}>
              <line x1={cx} x2={cx} y1={yHigh} y2={yLow} stroke={color} strokeWidth={1} />
              <rect x={cx - candleW / 2} y={bodyTop} width={candleW} height={bodyH} fill={color} opacity={0.85} />
            </g>
          )
        })}
      </svg>
    </section>
  )
}

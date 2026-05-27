import type { PairInfo, ScraperStatus } from '../api/types'

interface PairSelectorProps {
  pairs: PairInfo[]
  scrapers: ScraperStatus[]
  selected: string
  onSelect: (symbol: string) => void
}

function scraperTone(status: string) {
  if (status === 'live' || status === 'bootstrap') return 'ok'
  if (status === 'pending') return 'warn'
  return 'bad'
}

export function PairSelector({ pairs, scrapers, selected, onSelect }: PairSelectorProps) {
  const statusMap = Object.fromEntries(scrapers.map((s) => [s.symbol, s]))

  return (
    <aside className="panel pair-selector">
      <div className="panel-head">
        <h2>Pair Universe</h2>
        <span className="panel-tag">{pairs.length} pairs</span>
      </div>
      <ul className="pair-list">
        {pairs.map((pair) => {
          const scraper = statusMap[pair.symbol]
          const tone = scraper ? scraperTone(scraper.ohlcv) : 'warn'
          const active = pair.symbol === selected
          return (
            <li key={pair.symbol}>
              <button
                type="button"
                className={`pair-item ${active ? 'active' : ''}`}
                onClick={() => onSelect(pair.symbol)}
              >
                <div className="pair-item-top">
                  <span className="pair-symbol">{pair.symbol}</span>
                  <span className={`pair-dot dot-${tone}`} />
                </div>
                <span className="pair-class">{pair.asset_class}</span>
                <span className="pair-venue">{pair.ecn_venue}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </aside>
  )
}

import type { MacroResponse } from '../api/types'

interface MacroPanelProps {
  macro: MacroResponse | null
}

export function MacroPanel({ macro }: MacroPanelProps) {
  if (!macro) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Macro Anchor</h2></div>
        <div className="loading-block">Loading macro…</div>
      </section>
    )
  }

  const yields = Object.entries(macro.yields)

  return (
    <section className="panel macro-panel">
      <div className="panel-head">
        <div>
          <h2>Macro Anchor</h2>
          <p className="panel-sub">{macro.macro_anchor}</p>
        </div>
        <span className="panel-tag">{macro.source}</span>
      </div>

      {yields.length > 0 ? (
        <div className="macro-yields">
          {yields.map(([key, val]) => (
            <div key={key} className="macro-yield">
              <span>{key}</span>
              <strong className="mono">{val.toFixed(3)}%</strong>
            </div>
          ))}
        </div>
      ) : (
        <p className="panel-sub">Yield data pending scraper refresh</p>
      )}

      {macro.spread != null && (
        <div className="macro-spread">
          <span>2Y Spread</span>
          <strong className={`mono ${macro.spread >= 0 ? 'text-ok' : 'text-bad'}`}>
            {macro.spread >= 0 ? '+' : ''}{macro.spread.toFixed(3)} bps
          </strong>
        </div>
      )}
    </section>
  )
}

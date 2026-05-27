import { useCallback, useEffect, useState } from 'react'
import { api } from './api/client'
import type { PairInfo } from './api/types'
import { AnalyticsPanel } from './components/AnalyticsPanel'
import { CotPanel } from './components/CotPanel'
import { EntropyPanel } from './components/EntropyPanel'
import { ForecastPanel } from './components/ForecastPanel'
import { FuturesPanel } from './components/FuturesPanel'
import { GanttPanel } from './components/GanttPanel'
import { Header } from './components/Header'
import { HealthPanel } from './components/HealthPanel'
import { MacroPanel } from './components/MacroPanel'
import { PairSelector } from './components/PairSelector'
import { PivotsPanel } from './components/PivotsPanel'
import { PriceChart } from './components/PriceChart'
import { RiskDeskPanel } from './components/RiskDeskPanel'
import { SessionClock } from './components/SessionClock'
import { UniverseOverview } from './components/UniverseOverview'
import { VolumeProfilePanel } from './components/VolumeProfilePanel'
import { useDeskData } from './hooks/useDeskData'
import { useBackendStatus } from './hooks/useBackendStatus'
import { useHealth } from './hooks/useHealth'
import { useLiveStream } from './hooks/useLiveStream'
import { usePairData } from './hooks/usePairData'
import './App.css'

const DEFAULT_SYMBOL = 'GBPUSD'
type Tab = 'desk' | 'pair' | 'macro'

export default function App() {
  const [pairs, setPairs] = useState<PairInfo[]>([])
  const [selected, setSelected] = useState(DEFAULT_SYMBOL)
  const [liveEnabled, setLiveEnabled] = useState(true)
  const [tab, setTab] = useState<Tab>('desk')
  const [navOpen, setNavOpen] = useState(false)

  const { status: backend, check: checkBackend } = useBackendStatus()
  const { health, refresh: refreshHealth } = useHealth()
  const { data: desk, refresh: refreshDesk } = useDeskData()
  const { data, refresh: refreshPair, updateForecast } = usePairData(selected)
  const { connected } = useLiveStream(selected, liveEnabled, updateForecast)

  useEffect(() => {
    api.pairs()
      .then((res) => setPairs(res.pairs))
      .catch(() => setPairs([]))
  }, [])

  useEffect(() => {
    if (!navOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setNavOpen(false)
    }
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', onKey)
    }
  }, [navOpen])

  const handleRefresh = useCallback(() => {
    checkBackend()
    refreshHealth()
    refreshDesk()
    refreshPair()
  }, [checkBackend, refreshHealth, refreshDesk, refreshPair])

  const handleSelectPair = (symbol: string) => {
    setSelected(symbol)
    setTab('pair')
    setNavOpen(false)
  }

  const profile = data.profile ?? data.forecast?.volume_profile ?? null

  return (
    <div className="app">
      <Header
        health={health}
        backend={backend}
        selectedSymbol={selected}
        liveConnected={connected}
        onRefresh={handleRefresh}
        onOpenNav={() => setNavOpen(true)}
      />

      {!backend.connected && (
        <div className="error-banner">
          Backend offline at {import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'}.
          <span> Start it with: uvicorn aaim_terminal.main:app --host 127.0.0.1 --port 8000 --reload</span>
        </div>
      )}

      {backend.connected && !backend.hasDeskRoutes && (
        <div className="error-banner warn-banner">
          Backend is running an old version without desk routes.
          <span> Restart the backend to load the latest API.</span>
        </div>
      )}

      {(data.error || desk.error) && backend.connected && (
        <div className="error-banner">
          {data.error || desk.error}
          <span> — ensure the FastAPI backend is running on port 8000</span>
        </div>
      )}

      <SessionClock sessions={desk.sessions} />

      <nav className="tab-nav" aria-label="Main sections">
        <button type="button" className={tab === 'desk' ? 'active' : ''} onClick={() => setTab('desk')}>
          <span className="show-wide">Desk Overview</span>
          <span className="show-compact">Desk</span>
        </button>
        <button type="button" className={tab === 'pair' ? 'active' : ''} onClick={() => setTab('pair')}>
          <span className="show-wide">Pair Detail — {selected}</span>
          <span className="show-compact">{selected}</span>
        </button>
        <button type="button" className={tab === 'macro' ? 'active' : ''} onClick={() => setTab('macro')}>
          <span className="show-wide">Macro & Flow</span>
          <span className="show-compact">Macro</span>
        </button>
      </nav>

      <div className={`layout layout-${tab}`}>
        <button
          type="button"
          className={`pair-nav-backdrop ${navOpen ? 'open' : ''}`}
          aria-label="Close pair list"
          onClick={() => setNavOpen(false)}
          tabIndex={navOpen ? 0 : -1}
        />

        <PairSelector
          pairs={pairs}
          scrapers={health?.scrapers ?? []}
          selected={selected}
          open={navOpen}
          onSelect={handleSelectPair}
          onClose={() => setNavOpen(false)}
        />

        <main className="main-column">
          {tab === 'desk' && (
            <>
              <UniverseOverview
                overview={desk.overview}
                selected={selected}
                onSelect={handleSelectPair}
                loading={desk.loading}
              />
              <RiskDeskPanel risk={desk.risk} />
              <CotPanel cot={desk.cot} />
            </>
          )}

          {tab === 'pair' && (
            <>
              <PriceChart
                bars={data.bars}
                profile={profile}
                symbol={selected}
                entryLow={data.forecast?.entry_range?.low}
                entryHigh={data.forecast?.entry_range?.high}
                tp={data.forecast?.tp}
                sl={data.forecast?.sl}
              />
              <ForecastPanel
                forecast={data.forecast}
                analytics={data.analytics}
                loading={data.loading}
              />
              <AnalyticsPanel analytics={data.analytics} loading={data.loading} />
              <GanttPanel gantt={data.gantt} />
              <VolumeProfilePanel profile={profile} symbol={selected} loading={data.loading} />
            </>
          )}

          {tab === 'macro' && (
            <>
              <MacroPanel macro={data.macro} />
              <FuturesPanel futures={data.futures} />
              <CotPanel cot={desk.cot} />
            </>
          )}
        </main>

        <aside className="side-column">
          <EntropyPanel entropy={data.entropy ?? null} loading={data.loading} />
          <PivotsPanel pivots={data.pivots} symbol={selected} loading={data.loading} />
          <HealthPanel health={health} pairs={pairs} selected={selected} />

          <div className="panel live-toggle">
            <label className="toggle-row">
              <input
                type="checkbox"
                checked={liveEnabled}
                onChange={(e) => setLiveEnabled(e.target.checked)}
              />
              <span>WebSocket live stream</span>
            </label>
          </div>
        </aside>
      </div>
    </div>
  )
}

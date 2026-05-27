import type { HealthResponse } from '../api/types'
import type { BackendStatus } from '../hooks/useBackendStatus'

interface HeaderProps {
  health: HealthResponse | null
  backend: BackendStatus
  selectedSymbol: string
  liveConnected: boolean
  onRefresh: () => void
  onOpenNav: () => void
}

export function Header({ health, backend, selectedSymbol, liveConnected, onRefresh, onOpenNav }: HeaderProps) {
  const status = health?.status ?? 'unknown'
  const apiBase = import.meta.env.VITE_API_URL ?? '/api (proxy)'

  return (
    <header className="header">
      <div className="header-brand">
        <button type="button" className="btn-nav-toggle" onClick={onOpenNav} aria-label="Open pair list">
          <span aria-hidden="true">☰</span>
        </button>
        <div className="logo-mark">A</div>
        <div className="header-titles">
          <h1>AAIM Terminal</h1>
          <p className="show-wide">
            V8.3 · 8-Pair Core · Backend {backend.version ?? 'offline'} · {apiBase}
          </p>
          <p className="show-compact">
            V8.3 · {backend.version ?? 'offline'}
          </p>
        </div>
      </div>

      <div className="header-meta">
        <div className="header-chip">
          <span className={`status-dot ${backend.connected ? 'status-ok' : 'status-bad'}`} />
          <span className="show-wide">API {backend.connected ? 'Connected' : 'Offline'}</span>
          <span className="show-compact">{backend.connected ? 'API' : 'Off'}</span>
        </div>
        <div className="header-chip">
          <span className={`status-dot status-${status}`} />
          <span className="show-wide">System {status}</span>
          <span className="show-compact">{status}</span>
        </div>
        <div className="header-chip header-chip-live">
          <span className={`status-dot ${liveConnected ? 'status-ok' : 'status-degraded'}`} />
          <span className="show-wide">{selectedSymbol} {liveConnected ? 'Live' : 'Polling'}</span>
          <span className="show-compact">{selectedSymbol}</span>
        </div>
        <button type="button" className="btn-ghost btn-refresh" onClick={onRefresh} aria-label="Refresh data">
          <span className="show-wide">Refresh</span>
          <span className="show-compact">↻</span>
        </button>
      </div>
    </header>
  )
}

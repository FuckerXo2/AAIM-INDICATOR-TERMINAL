import type { HealthResponse } from '../api/types'
import type { BackendStatus } from '../hooks/useBackendStatus'

interface HeaderProps {
  health: HealthResponse | null
  backend: BackendStatus
  selectedSymbol: string
  liveConnected: boolean
  onRefresh: () => void
}

export function Header({ health, backend, selectedSymbol, liveConnected, onRefresh }: HeaderProps) {
  const status = health?.status ?? 'unknown'
  const apiBase = import.meta.env.VITE_API_URL ?? '/api (proxy)'

  return (
    <header className="header">
      <div className="header-brand">
        <div className="logo-mark">A</div>
        <div>
          <h1>AAIM Indicator Terminal</h1>
          <p>V8.3 · 8-Pair Core · Backend {backend.version ?? 'offline'} · {apiBase}</p>
        </div>
      </div>

      <div className="header-meta">
        <div className="header-chip">
          <span className={`status-dot ${backend.connected ? 'status-ok' : 'status-bad'}`} />
          API {backend.connected ? 'Connected' : 'Offline'}
        </div>
        <div className="header-chip">
          <span className={`status-dot status-${status}`} />
          System {status}
        </div>
        <div className="header-chip">
          <span className={`status-dot ${liveConnected ? 'status-ok' : 'status-degraded'}`} />
          {selectedSymbol} {liveConnected ? 'Live' : 'Polling'}
        </div>
        <button type="button" className="btn-ghost" onClick={onRefresh}>
          Refresh
        </button>
      </div>
    </header>
  )
}

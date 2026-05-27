import type { SessionResponse } from '../api/types'

interface SessionClockProps {
  sessions: SessionResponse | null
}

export function SessionClock({ sessions }: SessionClockProps) {
  if (!sessions) return null

  const ts = new Date(sessions.timestamp_wat).toLocaleTimeString('en-GB', {
    timeZone: 'Africa/Lagos',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <section className="panel session-panel">
      <div className="panel-head">
        <div>
          <h2>Session Clock</h2>
          <p className="panel-sub">{ts} WAT · Next: {sessions.next_session.name} @ {sessions.next_session.start}</p>
        </div>
        <div className="session-flags">
          {sessions.is_london_open && <span className="session-flag active">London Open</span>}
          {sessions.is_ny_overlap && <span className="session-flag active">NY Overlap</span>}
          {sessions.is_ny_close && <span className="session-flag warn">NY Close</span>}
        </div>
      </div>

      <div className="session-timeline">
        {sessions.all_sessions.map((s) => (
          <div key={s.name} className={`session-block priority-${s.priority} ${s.active ? 'active' : ''}`}>
            <div className="session-time">{s.start}–{s.end}</div>
            <div className="session-name">{s.name}</div>
            <div className="session-desc">{s.description}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

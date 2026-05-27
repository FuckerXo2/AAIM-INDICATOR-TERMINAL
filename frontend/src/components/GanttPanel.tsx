import type { GanttResponse } from '../api/types'

interface GanttPanelProps {
  gantt: GanttResponse | null
}

const TYPE_COLORS: Record<string, string> = {
  session: '#3b82f6',
  entry: '#22c55e',
  exit: '#6366f1',
  risk: '#ef4444',
  management: '#f59e0b',
  block: '#ef4444',
}

export function GanttPanel({ gantt }: GanttPanelProps) {
  if (!gantt) {
    return (
      <section className="panel">
        <div className="panel-head"><h2>Execution Gantt</h2></div>
        <div className="loading-block">Loading gantt…</div>
      </section>
    )
  }

  return (
    <section className="panel gantt-panel">
      <div className="panel-head">
        <div>
          <h2>Execution Gantt</h2>
          <p className="panel-sub">{gantt.scenario.replace(/_/g, ' ')}</p>
        </div>
        <span className={`panel-tag ${gantt.executable ? 'tag-ok' : 'tag-degraded'}`}>
          {gantt.executable ? 'Executable' : 'Not executable'}
        </span>
      </div>

      <div className="gantt-list">
        {gantt.events.map((event, i) => (
          <div key={i} className={`gantt-row priority-${event.priority}`}>
            <div className="gantt-time">
              {event.time_wat}
              {event.end_wat && event.end_wat !== event.time_wat ? ` – ${event.end_wat}` : ''}
            </div>
            <div className="gantt-marker" style={{ background: TYPE_COLORS[event.type] ?? '#7d8fa3' }} />
            <div className="gantt-body">
              <strong>{event.label}</strong>
              <span>{event.action}</span>
            </div>
            <span className="gantt-type">{event.type}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

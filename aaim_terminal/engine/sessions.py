"""Session window status for WAT trading desk."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

from aaim_terminal.config import LONDON_OPEN, NY_CLOSE_END, NY_CLOSE_START, NY_OVERLAP

WAT = ZoneInfo("Africa/Lagos")


@dataclass
class SessionWindow:
    name: str
    start: time
    end: time
    description: str
    priority: str


SESSIONS = [
    SessionWindow("London Open", time(8, 0), time(10, 0), "Primary institutional sweep window", "high"),
    SessionWindow("London/NY Overlap", time(13, 0), time(16, 0), "Highest intraday volume — re-evaluate POC", "high"),
    SessionWindow("NY Close", time(21, 0), time(22, 0), "Lock previous day OHLC for pivot anchor", "medium"),
    SessionWindow("Asia", time(0, 0), time(7, 0), "Reduced liquidity — mean-reversion bias", "low"),
]


def _in_window(now: time, start: time, end: time) -> bool:
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end


def current_session_status() -> dict:
    now = datetime.now(WAT)
    now_time = now.time().replace(tzinfo=None)

    active = []
    upcoming = []
    for session in SESSIONS:
        if _in_window(now_time, session.start, session.end):
            active.append(session)
        elif session.start > now_time:
            upcoming.append(session)

    upcoming.sort(key=lambda s: s.start)
    next_session = upcoming[0] if upcoming else SESSIONS[0]

    return {
        "timestamp_wat": now.isoformat(),
        "active_sessions": [
            {"name": s.name, "description": s.description, "priority": s.priority}
            for s in active
        ],
        "next_session": {
            "name": next_session.name,
            "start": next_session.start.strftime("%H:%M"),
            "description": next_session.description,
            "priority": next_session.priority,
        },
        "is_london_open": _in_window(now_time, LONDON_OPEN, time(10, 0)),
        "is_ny_overlap": _in_window(now_time, NY_OVERLAP, time(16, 0)),
        "is_ny_close": _in_window(now_time, NY_CLOSE_START, NY_CLOSE_END),
        "all_sessions": [
            {
                "name": s.name,
                "start": s.start.strftime("%H:%M"),
                "end": s.end.strftime("%H:%M"),
                "description": s.description,
                "priority": s.priority,
                "active": _in_window(now_time, s.start, s.end),
            }
            for s in SESSIONS
        ],
    }

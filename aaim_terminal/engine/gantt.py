"""Execution Gantt timeline builder."""

from __future__ import annotations

from typing import Any, Optional

from aaim_terminal.engine.sessions import SESSIONS
from aaim_terminal.models import ForecastResponse


def build_execution_gantt(symbol: str, forecast: ForecastResponse) -> dict[str, Any]:
    events: list[dict[str, Any]] = []

    for session in SESSIONS:
        events.append(
            {
                "time_wat": session.start.strftime("%H:%M"),
                "end_wat": session.end.strftime("%H:%M"),
                "label": session.name,
                "action": session.description,
                "priority": session.priority,
                "type": "session",
            }
        )

    if forecast.scenario != "STAND_ASIDE" and forecast.entry_range:
        events.append(
            {
                "time_wat": forecast.timestamp_wat.strftime("%H:%M"),
                "label": forecast.scenario.replace("_", " ").title(),
                "action": f"Entry {forecast.entry_range.low} – {forecast.entry_range.high}",
                "priority": "critical",
                "type": "entry",
                "tp": forecast.tp,
                "sl": forecast.sl,
            }
        )
        if forecast.tp:
            events.append(
                {
                    "time_wat": "—",
                    "label": "Take Profit",
                    "action": f"Target POC @ {forecast.tp}",
                    "priority": "high",
                    "type": "exit",
                }
            )
        if forecast.sl:
            events.append(
                {
                    "time_wat": "—",
                    "label": "Stop Loss",
                    "action": f"Hard stop @ {forecast.sl}",
                    "priority": "high",
                    "type": "risk",
                }
            )

    if forecast.regime == "Trend Expansion":
        events.append(
            {
                "time_wat": "Live",
                "label": "Trailing SL",
                "action": "Switch to VAH/VAL boundary trail",
                "priority": "medium",
                "type": "management",
            }
        )

    if not forecast.entropy.clearance:
        events.append(
            {
                "time_wat": "Now",
                "label": "Entropy Block",
                "action": "Stand aside — transition ambiguity",
                "priority": "critical",
                "type": "block",
            }
        )

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    events.sort(key=lambda e: priority_order.get(e["priority"], 9))

    return {
        "symbol": symbol,
        "scenario": forecast.scenario,
        "events": events,
        "executable": forecast.scenario != "STAND_ASIDE" and forecast.entropy.clearance,
    }

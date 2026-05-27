"""Institutional desk-level endpoints."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter

from aaim_terminal.config import PAIRS
from aaim_terminal.engine.analytics import compute_analytics
from aaim_terminal.engine.basilica import generate_forecast
from aaim_terminal.engine.sessions import current_session_status
from aaim_terminal.models import (
    CotPosition,
    CotResponse,
    DeskOverviewResponse,
    PairOverviewRow,
    RiskDeskResponse,
    SessionInfo,
    SessionResponse,
)
from aaim_terminal.scrapers.demo_data import generate_synthetic_bars
from aaim_terminal.storage.cache import store

router = APIRouter(prefix="/desk", tags=["desk"])
WAT = ZoneInfo("Africa/Lagos")


def _bars(symbol: str):
    bars = store.get_ohlcv(symbol)
    return bars if bars is not None and not bars.empty else generate_synthetic_bars(symbol)


@router.get("/overview", response_model=DeskOverviewResponse)
async def desk_overview() -> DeskOverviewResponse:
    rows: list[PairOverviewRow] = []
    circuit_breakers = 0
    for symbol, cfg in PAIRS.items():
        bars = _bars(symbol)
        forecast = generate_forecast(symbol, bars)
        analytics = compute_analytics(symbol, bars)
        if analytics["garch"]["circuit_breaker_active"]:
            circuit_breakers += 1
        actionable = forecast.scenario != "STAND_ASIDE" and forecast.entropy.clearance
        rows.append(
            PairOverviewRow(
                symbol=symbol,
                asset_class=cfg.asset_class,
                price=analytics["price"],
                change_pct=analytics["change_pct"],
                scenario=forecast.scenario,
                regime=forecast.regime,
                garch_regime=analytics["garch"]["regime"],
                entropy_bits=forecast.entropy.bits,
                clearance=forecast.entropy.clearance,
                position_size_multiplier=forecast.position_size_multiplier,
                mp_signals=forecast.mp_signals_retained,
                actionable=actionable,
            )
        )

    return DeskOverviewResponse(
        timestamp_wat=datetime.now(WAT).isoformat(),
        pairs=rows,
        actionable_count=sum(1 for r in rows if r.actionable),
        blocked_count=sum(1 for r in rows if not r.clearance),
        circuit_breaker_count=circuit_breakers,
    )


@router.get("/risk", response_model=RiskDeskResponse)
async def risk_desk() -> RiskDeskResponse:
    sessions = current_session_status()
    entropies: list[float] = []
    multipliers: list[float] = []
    stand_aside = bullish = bearish = entropy_blocked = circuit_breakers = 0
    at_risk: list[str] = []

    for symbol in PAIRS:
        bars = _bars(symbol)
        forecast = generate_forecast(symbol, bars)
        analytics = compute_analytics(symbol, bars)
        entropies.append(forecast.entropy.bits)
        multipliers.append(forecast.position_size_multiplier)

        if forecast.scenario == "STAND_ASIDE":
            stand_aside += 1
        elif forecast.scenario == "BULLISH_PULLBACK_SWEEP":
            bullish += 1
        else:
            bearish += 1

        if not forecast.entropy.clearance:
            entropy_blocked += 1
            at_risk.append(symbol)
        if analytics["garch"]["circuit_breaker_active"]:
            circuit_breakers += 1
            if symbol not in at_risk:
                at_risk.append(symbol)

    return RiskDeskResponse(
        timestamp_wat=datetime.now(WAT).isoformat(),
        total_pairs=len(PAIRS),
        stand_aside=stand_aside,
        bullish=bullish,
        bearish=bearish,
        entropy_blocked=entropy_blocked,
        circuit_breakers=circuit_breakers,
        avg_entropy=round(sum(entropies) / len(entropies), 3) if entropies else 0,
        avg_position_multiplier=round(sum(multipliers) / len(multipliers), 2) if multipliers else 1,
        high_priority_sessions_active=sessions["is_london_open"] or sessions["is_ny_overlap"],
        pairs_at_risk=at_risk,
    )


@router.get("/sessions", response_model=SessionResponse)
async def desk_sessions() -> SessionResponse:
    data = current_session_status()
    return SessionResponse(
        timestamp_wat=data["timestamp_wat"],
        active_sessions=data["active_sessions"],
        next_session=data["next_session"],
        is_london_open=data["is_london_open"],
        is_ny_overlap=data["is_ny_overlap"],
        is_ny_close=data["is_ny_close"],
        all_sessions=[SessionInfo(**s) for s in data["all_sessions"]],
    )


@router.get("/cot", response_model=CotResponse)
async def desk_cot() -> CotResponse:
    cot = store.get_cot()
    positions = []
    for currency, data in cot.items():
        net_long = float(data.get("net_long", 0))
        net_short = float(data.get("net_short", 0))
        net = net_long - net_short
        bias = "Net Long" if net > 0 else "Net Short" if net < 0 else "Neutral"
        positions.append(
            CotPosition(
                currency=currency,
                net_long=net_long,
                net_short=net_short,
                net_position=net,
                bias=bias,
                source=data.get("source", "unknown"),
                as_of=data.get("as_of"),
            )
        )
    return CotResponse(positions=positions, updated=datetime.now(WAT).isoformat())

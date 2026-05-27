"""Pair forecast, pivots, profile, and entropy endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from aaim_terminal.config import PAIRS, VALID_SYMBOLS
from aaim_terminal.engine.analytics import compute_analytics
from aaim_terminal.engine.basilica import generate_forecast
from aaim_terminal.engine.entropy_sentinel import compute_entropy_sentinel
from aaim_terminal.engine.gantt import build_execution_gantt
from aaim_terminal.engine.pivots import (
    compute_camarilla_pivots,
    compute_fibonacci_pivots,
    compute_standard_pivots,
    session_ohlc_from_bars,
)
from aaim_terminal.engine.volume_profile import compute_volume_profile
from aaim_terminal.models import (
    AnalyticsResponse,
    BarsResponse,
    EntropyResponse,
    ForecastResponse,
    FuturesResponse,
    GanttEvent,
    GanttResponse,
    GarchSnapshot,
    MacroResponse,
    MPFilterSnapshot,
    OHLCVBar,
    PairInfo,
    PairsListResponse,
    PivotWeightsSnapshot,
    PivotsResponse,
    VolumeProfileResponse,
)
from aaim_terminal.scrapers.demo_data import generate_synthetic_bars
from aaim_terminal.storage.cache import store

router = APIRouter(prefix="/pairs", tags=["pairs"])


def _validate_symbol(symbol: str) -> str:
    sym = symbol.upper()
    if sym not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Unknown pair: {symbol}. Valid: {sorted(VALID_SYMBOLS)}")
    return sym


def _get_bars(symbol: str):
    bars = store.get_ohlcv(symbol)
    if bars is None or bars.empty:
        bars = generate_synthetic_bars(symbol)
    return bars


@router.get("", response_model=PairsListResponse)
async def list_pairs() -> PairsListResponse:
    return PairsListResponse(
        pairs=[
            PairInfo(
                symbol=p.symbol,
                asset_class=p.asset_class,
                ecn_venue=p.ecn_venue,
                cme_futures_proxy=p.cme_futures_proxy,
                macro_anchor=p.macro_anchor,
            )
            for p in PAIRS.values()
        ]
    )


@router.get("/{symbol}/forecast", response_model=ForecastResponse)
async def get_forecast(symbol: str) -> ForecastResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym)
    return generate_forecast(sym, bars)


@router.get("/{symbol}/pivots", response_model=PivotsResponse)
async def get_pivots(symbol: str) -> PivotsResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym)
    ohlc = session_ohlc_from_bars(bars)
    return PivotsResponse(
        symbol=sym,
        standard=compute_standard_pivots(ohlc),
        camarilla=compute_camarilla_pivots(ohlc),
        fibonacci=compute_fibonacci_pivots(ohlc),
    )


@router.get("/{symbol}/profile", response_model=VolumeProfileResponse)
async def get_profile(symbol: str) -> VolumeProfileResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym)
    profile = compute_volume_profile(bars)
    return VolumeProfileResponse(symbol=sym, **profile.model_dump())


@router.get("/{symbol}/entropy", response_model=EntropyResponse)
async def get_entropy(symbol: str) -> EntropyResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym)
    entropy = compute_entropy_sentinel(bars)
    return EntropyResponse(
        symbol=sym,
        entropy_bits=entropy.bits,
        classification=entropy.classification,
        clearance=entropy.clearance,
    )


@router.get("/{symbol}/analytics", response_model=AnalyticsResponse)
async def get_analytics(symbol: str) -> AnalyticsResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym)
    data = compute_analytics(sym, bars)
    return AnalyticsResponse(
        symbol=sym,
        price=data["price"],
        change_pct=data["change_pct"],
        atr=data["atr"],
        atr_percentile=data["atr_percentile"],
        atr_regime=data["atr_regime"],
        garch=GarchSnapshot(**data["garch"]),
        mp_filter=MPFilterSnapshot(**data["mp_filter"]),
        pivot_weights=PivotWeightsSnapshot(**data["pivot_weights"]),
    )


@router.get("/{symbol}/bars", response_model=BarsResponse)
async def get_bars(symbol: str, limit: int = Query(default=60, ge=10, le=120)) -> BarsResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym).tail(limit)
    return BarsResponse(
        symbol=sym,
        bars=[
            OHLCVBar(
                timestamp=str(row["timestamp"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row.get("volume", 0)),
            )
            for _, row in bars.iterrows()
        ],
    )


@router.get("/{symbol}/macro", response_model=MacroResponse)
async def get_macro(symbol: str) -> MacroResponse:
    sym = _validate_symbol(symbol)
    cfg = PAIRS[sym]
    cached = store.get_macro(sym) or {}
    yields_raw = cached.get("yields", {})
    yields = {k: float(v) for k, v in yields_raw.items()} if yields_raw else {}
    spread = cached.get("spread")
    return MacroResponse(
        symbol=sym,
        macro_anchor=cfg.macro_anchor,
        yields=yields,
        spread=float(spread) if spread is not None else None,
        source=str(cached.get("source", "unknown")),
    )


@router.get("/{symbol}/futures", response_model=FuturesResponse)
async def get_futures(symbol: str) -> FuturesResponse:
    sym = _validate_symbol(symbol)
    cfg = PAIRS[sym]
    cached = store.get_futures(sym) or {}
    return FuturesResponse(
        symbol=sym,
        cme_proxy=cfg.cme_futures_proxy,
        volume=float(cached.get("volume", 0)),
        open_interest=float(cached.get("open_interest", 0)),
        source=str(cached.get("source", "unknown")),
    )


@router.get("/{symbol}/gantt", response_model=GanttResponse)
async def get_gantt(symbol: str) -> GanttResponse:
    sym = _validate_symbol(symbol)
    bars = _get_bars(sym)
    forecast = generate_forecast(sym, bars)
    gantt = build_execution_gantt(sym, forecast)
    return GanttResponse(
        symbol=sym,
        scenario=gantt["scenario"],
        events=[GanttEvent(**e) for e in gantt["events"]],
        executable=gantt["executable"],
    )

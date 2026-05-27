"""Pydantic schemas for AAIM V8.3 API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PivotLevels(BaseModel):
    P: Optional[float] = None
    R1: Optional[float] = None
    R2: Optional[float] = None
    R3: Optional[float] = None
    R4: Optional[float] = None
    S1: Optional[float] = None
    S2: Optional[float] = None
    S3: Optional[float] = None
    S4: Optional[float] = None


class PivotsResponse(BaseModel):
    symbol: str
    anchor: str = "previous_ny_close_22:00_wat"
    standard: PivotLevels
    camarilla: PivotLevels
    fibonacci: PivotLevels


class VolumeProfileResponse(BaseModel):
    symbol: str
    POC: float
    VAH: float
    VAL: float
    LVN: float


class EntropyResponse(BaseModel):
    symbol: str
    entropy_bits: float
    classification: str
    clearance: bool


class EntryRange(BaseModel):
    low: float
    high: float


class VolumeProfileSnapshot(BaseModel):
    POC: float
    VAH: float
    VAL: float
    LVN: float


class EntropySnapshot(BaseModel):
    bits: float
    classification: str
    clearance: bool


ScenarioLabel = Literal["BULLISH_PULLBACK_SWEEP", "BEARISH_SUPPLY_REJECTION", "STAND_ASIDE"]


class ForecastResponse(BaseModel):
    symbol: str
    timestamp_wat: datetime
    scenario: ScenarioLabel
    entry_range: Optional[EntryRange] = None
    tp: Optional[float] = None
    sl: Optional[float] = None
    volume_profile: VolumeProfileSnapshot
    entropy: EntropySnapshot
    regime: str
    mp_signals_retained: int
    position_size_multiplier: float = Field(default=1.0, ge=0.0, le=1.0)


class ScraperStatus(BaseModel):
    symbol: str
    ohlcv: str
    last_bar_age_seconds: Optional[float] = None
    futures: str
    yield_scraper: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    scrapers: list[ScraperStatus]
    pairs_monitored: int = 8


class PairInfo(BaseModel):
    symbol: str
    asset_class: str
    ecn_venue: str
    cme_futures_proxy: str
    macro_anchor: str


class PairsListResponse(BaseModel):
    pairs: list[PairInfo]


class OHLCVBar(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class BarsResponse(BaseModel):
    symbol: str
    interval: str = "15m"
    bars: list[OHLCVBar]


class GarchSnapshot(BaseModel):
    conditional_variance: float
    percentile: float
    regime: str
    position_size_multiplier: float
    block_breakout_entries: bool
    circuit_breaker_active: bool


class MPFilterSnapshot(BaseModel):
    signals_retained: int
    noise_ceiling: float
    max_lags: int
    gamma: float


class PivotWeightsSnapshot(BaseModel):
    standard: float
    camarilla: float
    fibonacci: float
    volume_profile: float


class AnalyticsResponse(BaseModel):
    symbol: str
    price: float
    change_pct: float
    atr: float
    atr_percentile: float
    atr_regime: str
    garch: GarchSnapshot
    mp_filter: MPFilterSnapshot
    pivot_weights: PivotWeightsSnapshot


class MacroResponse(BaseModel):
    symbol: str
    macro_anchor: str
    yields: dict[str, float]
    spread: Optional[float] = None
    source: str = "unknown"


class FuturesResponse(BaseModel):
    symbol: str
    cme_proxy: str
    volume: float
    open_interest: float
    source: str


class CotPosition(BaseModel):
    currency: str
    net_long: float
    net_short: float
    net_position: float
    bias: str
    source: str
    as_of: Optional[str] = None


class CotResponse(BaseModel):
    positions: list[CotPosition]
    updated: Optional[str] = None


class GanttEvent(BaseModel):
    time_wat: str
    end_wat: Optional[str] = None
    label: str
    action: str
    priority: str
    type: str
    tp: Optional[float] = None
    sl: Optional[float] = None


class GanttResponse(BaseModel):
    symbol: str
    scenario: str
    events: list[GanttEvent]
    executable: bool


class SessionInfo(BaseModel):
    name: str
    start: str
    end: str
    description: str
    priority: str
    active: bool


class SessionResponse(BaseModel):
    timestamp_wat: str
    active_sessions: list[dict]
    next_session: dict
    is_london_open: bool
    is_ny_overlap: bool
    is_ny_close: bool
    all_sessions: list[SessionInfo]


class PairOverviewRow(BaseModel):
    symbol: str
    asset_class: str
    price: float
    change_pct: float
    scenario: str
    regime: str
    garch_regime: str
    entropy_bits: float
    clearance: bool
    position_size_multiplier: float
    mp_signals: int
    actionable: bool


class DeskOverviewResponse(BaseModel):
    timestamp_wat: str
    pairs: list[PairOverviewRow]
    actionable_count: int
    blocked_count: int
    circuit_breaker_count: int


class RiskDeskResponse(BaseModel):
    timestamp_wat: str
    total_pairs: int
    stand_aside: int
    bullish: int
    bearish: int
    entropy_blocked: int
    circuit_breakers: int
    avg_entropy: float
    avg_position_multiplier: float
    high_priority_sessions_active: bool
    pairs_at_risk: list[str]


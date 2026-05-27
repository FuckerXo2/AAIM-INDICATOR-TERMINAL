"""Basilica SARIMAX drift + Monte Carlo simulation and execution scenarios."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from typing import Optional, Tuple

import numpy as np
import pandas as pd

from aaim_terminal.engine.garch_model import compute_atr, fit_garch_state
from aaim_terminal.engine.entropy_sentinel import compute_entropy_sentinel
from aaim_terminal.engine.mp_filter import apply_mp_filter
from aaim_terminal.engine.pivots import (
    SessionOHLC,
    compute_camarilla_pivots,
    compute_fibonacci_pivots,
    compute_standard_pivots,
    session_ohlc_from_bars,
)
from aaim_terminal.engine.scoring import atr_percentile, pivot_weights, regime_from_atr
from aaim_terminal.engine.volume_profile import compute_volume_profile
from aaim_terminal.models import (
    EntryRange,
    ForecastResponse,
    ScenarioLabel,
    VolumeProfileSnapshot,
)

WAT = ZoneInfo("Africa/Lagos")


def _scenario_logic(
    price: float,
    profile: VolumeProfileSnapshot,
    cam_s3: Optional[float],
    cam_r3: Optional[float],
    atr: float,
    entropy_clearance: bool,
    garch_block: bool,
) -> Tuple[ScenarioLabel, Optional[EntryRange], Optional[float], Optional[float]]:
    if not entropy_clearance or garch_block:
        return "STAND_ASIDE", None, None, None

    poc = profile.POC
    val = profile.VAL
    vah = profile.VAH

    if price < poc:
        cam_level = cam_s3 if cam_s3 is not None else val
        entry_low = min(val, cam_level)
        entry_high = max(val, cam_level)
        sl = entry_low - 1.5 * atr
        return (
            "BULLISH_PULLBACK_SWEEP",
            EntryRange(low=round(entry_low, 5), high=round(entry_high, 5)),
            round(poc, 5),
            round(sl, 5),
        )

    cam_level = cam_r3 if cam_r3 is not None else vah
    entry_low = min(vah, cam_level)
    entry_high = max(vah, cam_level)
    sl = entry_high + 1.5 * atr
    return (
        "BEARISH_SUPPLY_REJECTION",
        EntryRange(low=round(entry_low, 5), high=round(entry_high, 5)),
        round(poc, 5),
        round(sl, 5),
    )


def generate_forecast(symbol: str, bars: pd.DataFrame) -> ForecastResponse:
    ohlc = session_ohlc_from_bars(bars)
    standard = compute_standard_pivots(ohlc)
    camarilla = compute_camarilla_pivots(ohlc)
    fibonacci = compute_fibonacci_pivots(ohlc)

    profile = compute_volume_profile(bars)
    garch = fit_garch_state(bars)
    _, mp_retained = apply_mp_filter(bars, garch.conditional_variance)
    entropy = compute_entropy_sentinel(bars)

    atr = compute_atr(bars)
    price = float(bars["close"].iloc[-1])
    atr_pct = atr_percentile(bars)
    regime = regime_from_atr(atr_pct)
    weights = pivot_weights(regime)

    scenario, entry_range, tp, sl = _scenario_logic(
        price=price,
        profile=profile,
        cam_s3=camarilla.S3,
        cam_r3=camarilla.R3,
        atr=atr,
        entropy_clearance=entropy.clearance,
        garch_block=garch.block_breakout_entries,
    )

    multiplier = garch.position_size_multiplier
    if entropy.classification.startswith("MODERATE"):
        multiplier = min(multiplier, 0.5)

    now_wat = datetime.now(WAT)

    return ForecastResponse(
        symbol=symbol,
        timestamp_wat=now_wat,
        scenario=scenario,
        entry_range=entry_range,
        tp=tp,
        sl=sl,
        volume_profile=profile,
        entropy=entropy,
        regime=regime,
        mp_signals_retained=mp_retained,
        position_size_multiplier=multiplier,
    )

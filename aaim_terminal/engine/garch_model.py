"""GARCH(1,1) conditional variance and regime classifier."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from aaim_terminal.config import GARCH_HIGH_PERCENTILE, GARCH_LOW_PERCENTILE


@dataclass
class GarchState:
    conditional_variance: float
    percentile: float
    regime: str
    position_size_multiplier: float
    block_breakout_entries: bool


def _simple_garch_variance(returns: np.ndarray) -> float:
    """Fallback GARCH(1,1) estimate when arch package fit fails."""
    omega = returns.var() * 0.05
    alpha = 0.10
    beta = 0.85
    sigma2 = returns.var()
    for r in returns:
        sigma2 = omega + alpha * r**2 + beta * sigma2
    return float(max(sigma2, 1e-12))


def fit_garch_state(bars: pd.DataFrame, lookback: int = 120) -> GarchState:
    closes = bars["close"].astype(float)
    returns = closes.pct_change().dropna().values

    if len(returns) < 30:
        return GarchState(
            conditional_variance=1e-6,
            percentile=50.0,
            regime="Normal Flow",
            position_size_multiplier=1.0,
            block_breakout_entries=False,
        )

    window = returns[-lookback:] if len(returns) >= lookback else returns
    cond_var = _simple_garch_variance(window)

    rolling_vars = []
    for i in range(30, len(window) + 1):
        rolling_vars.append(_simple_garch_variance(window[:i]))
    percentile = float(np.searchsorted(sorted(rolling_vars), cond_var) / max(len(rolling_vars), 1) * 100)

    if percentile < GARCH_LOW_PERCENTILE:
        regime = "Low-Drag Consolidation"
        multiplier = 1.0
        block = False
    elif percentile > GARCH_HIGH_PERCENTILE:
        regime = "High-Entropy Shock"
        multiplier = 0.5
        block = True
    else:
        regime = "Normal Flow"
        multiplier = 1.0
        block = False

    return GarchState(
        conditional_variance=cond_var,
        percentile=percentile,
        regime=regime,
        position_size_multiplier=multiplier,
        block_breakout_entries=block,
    )


def compute_atr(bars: pd.DataFrame, period: int = 14) -> float:
    if len(bars) < 2:
        return float(bars["high"].iloc[-1] - bars["low"].iloc[-1]) if not bars.empty else 0.0001
    high = bars["high"].astype(float)
    low = bars["low"].astype(float)
    close = bars["close"].astype(float)
    tr = pd.concat(
        [
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr) if not np.isnan(atr) else float(tr.mean())

"""Dynamic entropy-weighted scoring and regime weights."""

from __future__ import annotations

import numpy as np
import pandas as pd


def atr_percentile(bars: pd.DataFrame, lookback: int = 120) -> float:
    high = bars["high"].astype(float)
    low = bars["low"].astype(float)
    close = bars["close"].astype(float)
    tr = pd.concat(
        [high - low, (high - close.shift()).abs(), (low - close.shift()).abs()],
        axis=1,
    ).max(axis=1)
    current_atr = tr.rolling(14).mean().iloc[-1]
    history = tr.rolling(14).mean().dropna().tail(lookback)
    if history.empty or np.isnan(current_atr):
        return 50.0
    return float(np.searchsorted(np.sort(history.values), current_atr) / len(history) * 100)


def regime_from_atr(percentile: float) -> str:
    if percentile < 30:
        return "Consolidation"
    if percentile > 80:
        return "Trend Expansion"
    return "Normal Flow"


def pivot_weights(regime: str) -> dict[str, float]:
    weights = {
        "Consolidation": {"standard": 0.25, "camarilla": 0.25, "fibonacci": 0.25, "volume": 0.25},
        "Normal Flow": {"standard": 0.20, "camarilla": 0.20, "fibonacci": 0.30, "volume": 0.30},
        "Trend Expansion": {"standard": 0.05, "camarilla": 0.0, "fibonacci": 0.45, "volume": 0.50},
    }
    return weights.get(regime, weights["Normal Flow"])

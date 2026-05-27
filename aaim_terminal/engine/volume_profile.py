"""POC / VAH / VAL / LVN volume profile calculator."""

from __future__ import annotations

import numpy as np
import pandas as pd

from aaim_terminal.models import VolumeProfileSnapshot


def compute_volume_profile(
    bars: pd.DataFrame,
    value_area_pct: float = 0.70,
    bins: int = 50,
) -> VolumeProfileSnapshot:
    if bars.empty or len(bars) < 5:
        mid = float(bars["close"].iloc[-1]) if not bars.empty else 1.0
        spread = mid * 0.001
        return VolumeProfileSnapshot(
            POC=round(mid, 5),
            VAH=round(mid + spread, 5),
            VAL=round(mid - spread, 5),
            LVN=round(mid - spread * 1.5, 5),
        )

    prices = ((bars["high"] + bars["low"] + bars["close"]) / 3).values
    volumes = bars["volume"].values if "volume" in bars.columns else np.ones(len(bars))
    if volumes.sum() <= 0:
        volumes = np.ones(len(bars))

    price_min, price_max = prices.min(), prices.max()
    if price_max == price_min:
        price_max = price_min + 1e-5

    edges = np.linspace(price_min, price_max, bins + 1)
    hist, _ = np.histogram(prices, bins=edges, weights=volumes)
    centers = (edges[:-1] + edges[1:]) / 2

    poc_idx = int(np.argmax(hist))
    poc = float(centers[poc_idx])

    total_vol = hist.sum()
    target = total_vol * value_area_pct
    va_indices = {poc_idx}
    accumulated = hist[poc_idx]

    lo, hi = poc_idx - 1, poc_idx + 1
    while accumulated < target and (lo >= 0 or hi < len(hist)):
        vol_lo = hist[lo] if lo >= 0 else -1
        vol_hi = hist[hi] if hi < len(hist) else -1
        if vol_lo >= vol_hi and lo >= 0:
            va_indices.add(lo)
            accumulated += hist[lo]
            lo -= 1
        elif hi < len(hist):
            va_indices.add(hi)
            accumulated += hist[hi]
            hi += 1
        else:
            break

    va_prices = centers[list(va_indices)]
    vah = float(va_prices.max())
    val = float(va_prices.min())

    # LVN: lowest volume bin adjacent to POC
    lvn_candidates = []
    for idx in range(max(0, poc_idx - 3), min(len(hist), poc_idx + 4)):
        if idx != poc_idx:
            lvn_candidates.append((hist[idx], centers[idx]))
    lvn = float(min(lvn_candidates, key=lambda x: x[0])[1]) if lvn_candidates else val

    return VolumeProfileSnapshot(
        POC=round(poc, 5),
        VAH=round(vah, 5),
        VAL=round(val, 5),
        LVN=round(lvn, 5),
    )

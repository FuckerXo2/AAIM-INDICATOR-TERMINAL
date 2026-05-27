"""Synthetic OHLCV seed data for demo / fallback when scrapers unavailable."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

# Approximate mid prices per pair for realistic synthetic bars
BASE_PRICES: dict[str, float] = {
    "EURUSD": 1.0850,
    "GBPUSD": 1.2750,
    "GBPJPY": 195.50,
    "EURGBP": 0.8510,
    "AUDUSD": 0.6520,
    "AUDCHF": 0.5780,
    "GBPCHF": 1.1320,
    "EURCHF": 0.9630,
}


def generate_synthetic_bars(symbol: str, n_bars: int = 120, interval_minutes: int = 15) -> pd.DataFrame:
    """Generate realistic 15m OHLCV bars for engine computation."""
    rng = np.random.default_rng(hash(symbol) % (2**32))
    base = BASE_PRICES.get(symbol, 1.0)
    pip = 0.01 if "JPY" in symbol else 0.0001

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    minutes = (now.minute // interval_minutes) * interval_minutes
    now = now.replace(minute=minutes)

    timestamps = [now - timedelta(minutes=interval_minutes * i) for i in range(n_bars - 1, -1, -1)]

    returns = rng.normal(0, pip * 3, n_bars)
    closes = base + np.cumsum(returns)
    opens = np.roll(closes, 1)
    opens[0] = base
    highs = np.maximum(opens, closes) + rng.uniform(pip, pip * 8, n_bars)
    lows = np.minimum(opens, closes) - rng.uniform(pip, pip * 8, n_bars)
    volumes = rng.integers(500, 5000, n_bars).astype(float)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }
    )

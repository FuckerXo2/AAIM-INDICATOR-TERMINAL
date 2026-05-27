"""Full pair analytics bundle for institutional desk."""

from __future__ import annotations

from typing import Any

import pandas as pd

from aaim_terminal.engine.garch_model import compute_atr, fit_garch_state
from aaim_terminal.engine.mp_filter import apply_mp_filter, mp_noise_ceiling
from aaim_terminal.engine.scoring import atr_percentile, pivot_weights, regime_from_atr
from aaim_terminal.config import MP_MAX_LAGS


def compute_analytics(symbol: str, bars: pd.DataFrame) -> dict[str, Any]:
    garch = fit_garch_state(bars)
    _, mp_retained = apply_mp_filter(bars, garch.conditional_variance)
    atr = compute_atr(bars)
    atr_pct = atr_percentile(bars)
    atr_regime = regime_from_atr(atr_pct)
    weights = pivot_weights(atr_regime)
    price = float(bars["close"].iloc[-1])
    prev = float(bars["close"].iloc[-2]) if len(bars) > 1 else price
    change_pct = ((price - prev) / prev) * 100 if prev else 0.0

    returns = bars["close"].pct_change().dropna().values
    ceiling = mp_noise_ceiling(len(returns[-120:]) if len(returns) >= 120 else len(returns), MP_MAX_LAGS, garch.conditional_variance)

    return {
        "symbol": symbol,
        "price": round(price, 5),
        "change_pct": round(change_pct, 4),
        "atr": round(atr, 5),
        "atr_percentile": round(atr_pct, 1),
        "atr_regime": atr_regime,
        "garch": {
            "conditional_variance": round(garch.conditional_variance, 8),
            "percentile": round(garch.percentile, 1),
            "regime": garch.regime,
            "position_size_multiplier": garch.position_size_multiplier,
            "block_breakout_entries": garch.block_breakout_entries,
            "circuit_breaker_active": garch.regime == "High-Entropy Shock",
        },
        "mp_filter": {
            "signals_retained": mp_retained,
            "noise_ceiling": round(ceiling, 6),
            "max_lags": MP_MAX_LAGS,
            "gamma": round(MP_MAX_LAGS / 120, 3),
        },
        "pivot_weights": {
            "standard": weights["standard"],
            "camarilla": weights["camarilla"],
            "fibonacci": weights["fibonacci"],
            "volume_profile": weights["volume"],
        },
    }

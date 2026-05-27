"""Temporal Marchenko-Pastur noise firewall."""

from __future__ import annotations

import numpy as np
import pandas as pd

from aaim_terminal.config import MP_MAX_LAGS


def build_lagged_matrix(returns: np.ndarray, max_lags: int = MP_MAX_LAGS) -> np.ndarray:
    """Build lagged return matrix for RMT analysis."""
    n = len(returns)
    if n <= max_lags:
        return returns.reshape(-1, 1)
    cols = []
    for lag in range(max_lags):
        cols.append(returns[lag : n - max_lags + lag])
    return np.column_stack(cols)


def mp_noise_ceiling(n_samples: int, max_lags: int, garch_variance: float) -> float:
    """Dynamic MP threshold with GARCH volatility expansion."""
    gamma = max_lags / max(n_samples, 1)
    base = (1 + np.sqrt(gamma)) ** 2
    vol_expansion = 1.0 + min(garch_variance * 1e4, 2.0)
    return base * vol_expansion


def apply_mp_filter(bars: pd.DataFrame, garch_variance: float) -> tuple[np.ndarray, int]:
    """Filter return structure eigenvalues below MP threshold."""
    returns = bars["close"].pct_change().dropna().values
    if len(returns) < MP_MAX_LAGS + 10:
        return returns, 0

    window = returns[-120:]
    mat = build_lagged_matrix(window, MP_MAX_LAGS)
    cov = np.cov(mat, rowvar=False)
    eigenvalues = np.linalg.eigvalsh(cov)
    ceiling = mp_noise_ceiling(len(window), MP_MAX_LAGS, garch_variance)

    retained_count = int((eigenvalues > ceiling).sum())
    if retained_count == 0:
        return returns, 0

    signal_ratio = float(eigenvalues[eigenvalues > ceiling].sum() / max(eigenvalues.sum(), 1e-12))
    denoised = returns * min(signal_ratio, 1.0)
    return denoised, retained_count

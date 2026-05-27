"""Shannon entropy risk sentinel."""

from __future__ import annotations

import numpy as np
import pandas as pd

from aaim_terminal.config import ENTROPY_HIGH, ENTROPY_LOW
from aaim_terminal.models import EntropySnapshot


def _shannon_entropy(probs: np.ndarray) -> float:
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 1.0
    return float(-np.sum(probs * np.log2(probs)))


def classify_entropy(bits: float) -> tuple[str, bool]:
    if bits <= ENTROPY_LOW:
        return "LOW_RISK_HIGH_CONVICTION_STABLE", True
    if bits <= ENTROPY_HIGH:
        return "MODERATE_RISK_REDUCED_SIZING_ZONE", True
    return "HIGH_RISK_TRANSITION_AMBIGUITY_AVOID", False


def compute_entropy_sentinel(bars: pd.DataFrame, n_states: int = 3) -> EntropySnapshot:
    returns = bars["close"].pct_change().dropna().values
    if len(returns) < 20:
        return EntropySnapshot(bits=0.35, classification="LOW_RISK_HIGH_CONVICTION_STABLE", clearance=True)

    recent = returns[-24:]
    hist, _ = np.histogram(recent, bins=n_states, density=True)
    hist = hist / hist.sum() if hist.sum() > 0 else np.ones(n_states) / n_states

    bits = _shannon_entropy(hist)
    classification, clearance = classify_entropy(bits)
    return EntropySnapshot(bits=round(bits, 3), classification=classification, clearance=clearance)

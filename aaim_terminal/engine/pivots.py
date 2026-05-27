"""Standard, Camarilla, and Fibonacci pivot calculators."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from aaim_terminal.models import PivotLevels


@dataclass
class SessionOHLC:
    high: float
    low: float
    close: float


def compute_standard_pivots(ohlc: SessionOHLC) -> PivotLevels:
    h, l, c = ohlc.high, ohlc.low, ohlc.close
    p = (h + l + c) / 3
    return PivotLevels(
        P=round(p, 5),
        R1=round((2 * p) - l, 5),
        S1=round((2 * p) - h, 5),
        R2=round(p + (h - l), 5),
        S2=round(p - (h - l), 5),
        R3=round(h + 2 * (p - l), 5),
        S3=round(l - 2 * (h - p), 5),
    )


def compute_camarilla_pivots(ohlc: SessionOHLC) -> PivotLevels:
    h, l, c = ohlc.high, ohlc.low, ohlc.close
    rng = h - l
    return PivotLevels(
        R4=round(c + rng * (1.1 / 2), 5),
        R3=round(c + rng * (1.1 / 4), 5),
        R2=round(c + rng * (1.1 / 6), 5),
        R1=round(c + rng * (1.1 / 12), 5),
        S1=round(c - rng * (1.1 / 12), 5),
        S2=round(c - rng * (1.1 / 6), 5),
        S3=round(c - rng * (1.1 / 4), 5),
        S4=round(c - rng * (1.1 / 2), 5),
    )


def compute_fibonacci_pivots(ohlc: SessionOHLC) -> PivotLevels:
    h, l, c = ohlc.high, ohlc.low, ohlc.close
    p = (h + l + c) / 3
    rng = h - l
    return PivotLevels(
        P=round(p, 5),
        R1=round(p + 0.382 * rng, 5),
        S1=round(p - 0.382 * rng, 5),
        R2=round(p + 0.618 * rng, 5),
        S2=round(p - 0.618 * rng, 5),
        R3=round(p + 1.000 * rng, 5),
        S3=round(p - 1.000 * rng, 5),
    )


def session_ohlc_from_bars(bars: pd.DataFrame) -> SessionOHLC:
    """Derive previous NY Close session OHLC from 15m bars."""
    if bars.empty:
        raise ValueError("Cannot compute pivots from empty bar history")
    return SessionOHLC(
        high=float(bars["high"].max()),
        low=float(bars["low"].min()),
        close=float(bars["close"].iloc[-1]),
    )

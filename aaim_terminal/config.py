"""Pair registry and session configuration for AAIM V8.3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Literal, Optional

AssetClass = Literal["Major", "Minor"]
Regime = Literal["Consolidation", "Normal Flow", "Trend Expansion"]


@dataclass(frozen=True)
class PairConfig:
    symbol: str
    asset_class: AssetClass
    ecn_venue: str
    cme_futures_proxy: str
    macro_anchor: str
    investing_slug: str
    cftc_code: Optional[str] = None
    investing_curr_id: Optional[int] = None


PAIRS: dict[str, PairConfig] = {
    "EURUSD": PairConfig(
        symbol="EURUSD",
        asset_class="Major",
        ecn_venue="EBS Primary Pool",
        cme_futures_proxy="6E=F",
        macro_anchor="DE02Y vs US02Y spread",
        investing_slug="eur-usd",
        cftc_code="099741",
        investing_curr_id=1,
    ),
    "GBPUSD": PairConfig(
        symbol="GBPUSD",
        asset_class="Major",
        ecn_venue="Refinitiv Matching",
        cme_futures_proxy="6B=F",
        macro_anchor="GB02Y vs US02Y spread",
        investing_slug="gbp-usd",
        cftc_code="096742",
        investing_curr_id=2,
    ),
    "GBPJPY": PairConfig(
        symbol="GBPJPY",
        asset_class="Minor",
        ecn_venue="Refinitiv Matching",
        cme_futures_proxy="6B=F",
        macro_anchor="FTSE 100 equity proxy",
        investing_slug="gbp-jpy",
        cftc_code="096742",
        investing_curr_id=7,
    ),
    "EURGBP": PairConfig(
        symbol="EURGBP",
        asset_class="Minor",
        ecn_venue="Refinitiv Matching",
        cme_futures_proxy="6E=F",
        macro_anchor="DE02Y vs GB02Y spread",
        investing_slug="eur-gbp",
        cftc_code="099741",
        investing_curr_id=6,
    ),
    "AUDUSD": PairConfig(
        symbol="AUDUSD",
        asset_class="Major",
        ecn_venue="Refinitiv Matching",
        cme_futures_proxy="6A=F",
        macro_anchor="Iron Ore Spot Index",
        investing_slug="aud-usd",
        cftc_code="112741",
        investing_curr_id=5,
    ),
    "AUDCHF": PairConfig(
        symbol="AUDCHF",
        asset_class="Minor",
        ecn_venue="EBS / Refinitiv",
        cme_futures_proxy="6A=F",
        macro_anchor="AUD risk + CHF haven composite",
        investing_slug="aud-chf",
        investing_curr_id=48,
    ),
    "GBPCHF": PairConfig(
        symbol="GBPCHF",
        asset_class="Minor",
        ecn_venue="Refinitiv Matching",
        cme_futures_proxy="6B=F",
        macro_anchor="GB02Y vs CH02Y spread",
        investing_slug="gbp-chf",
        investing_curr_id=12,
    ),
    "EURCHF": PairConfig(
        symbol="EURCHF",
        asset_class="Minor",
        ecn_venue="EBS Primary Pool",
        cme_futures_proxy="6E=F",
        macro_anchor="DE02Y vs CH02Y spread",
        investing_slug="eur-chf",
        investing_curr_id=10,
    ),
}

VALID_SYMBOLS = frozenset(PAIRS.keys())

# Session windows (WAT = UTC+1)
LONDON_OPEN = time(8, 0)
NY_OVERLAP = time(13, 0)
NY_CLOSE_START = time(21, 0)
NY_CLOSE_END = time(22, 0)

SCRAPER_TIMEOUT_MS = 200
OHLCV_REFRESH_SECONDS = 60
FUTURES_REFRESH_SECONDS = 300
OHLCV_STAGGER_SECONDS = 7.5
MAX_BAR_AGE_SECONDS = 90

# MP filter
MP_MAX_LAGS = 24
MP_LOOKBACK = 120
MP_GAMMA = MP_MAX_LAGS / MP_LOOKBACK

# Entropy thresholds (bits)
ENTROPY_LOW = 0.40
ENTROPY_HIGH = 0.85

# GARCH regime percentiles
GARCH_LOW_PERCENTILE = 30
GARCH_HIGH_PERCENTILE = 80

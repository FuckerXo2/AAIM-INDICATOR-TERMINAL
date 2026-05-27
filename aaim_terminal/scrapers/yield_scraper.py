"""Sovereign 2Y yield scraper for macro anchors."""

from __future__ import annotations

import logging
import re

import httpx

logger = logging.getLogger(__name__)

YIELD_PAGES = {
    "DE02Y": "https://www.investing.com/rates-bonds/germany-2-year-bond-yield",
    "US02Y": "https://www.investing.com/rates-bonds/united-states-2-year-bond-yield",
    "GB02Y": "https://www.investing.com/rates-bonds/united-kingdom-2-year-bond-yield",
    "CH02Y": "https://www.investing.com/rates-bonds/switzerland-2-year-bond-yield",
    "AU02Y": "https://www.investing.com/rates-bonds/australia-2-year-bond-yield",
}

FALLBACK_YIELDS = {
    "DE02Y": 2.45,
    "US02Y": 4.85,
    "GB02Y": 4.12,
    "CH02Y": 1.05,
    "AU02Y": 4.02,
}

PAIR_YIELD_MAP: dict[str, list[str]] = {
    "EURUSD": ["DE02Y", "US02Y"],
    "GBPUSD": ["GB02Y", "US02Y"],
    "GBPJPY": ["GB02Y"],
    "EURGBP": ["DE02Y", "GB02Y"],
    "AUDUSD": ["AU02Y"],
    "AUDCHF": ["AU02Y", "CH02Y"],
    "GBPCHF": ["GB02Y", "CH02Y"],
    "EURCHF": ["DE02Y", "CH02Y"],
}


async def _scrape_yield(key: str) -> float:
    url = YIELD_PAGES.get(key)
    if not url:
        return FALLBACK_YIELDS.get(key, 2.0)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            match = re.search(r'data-test="instrument-price-last">([\d.]+)', resp.text)
            if match:
                return float(match.group(1))
    except Exception as exc:
        logger.warning("Yield scrape failed for %s: %s", key, exc)
    return FALLBACK_YIELDS[key]


async def fetch_macro_spread(symbol: str) -> Dict[str, Union[float, str, None]]:
    keys = PAIR_YIELD_MAP.get(symbol, [])
    yields = {k: await _scrape_yield(k) for k in keys}
    spread = None
    if len(keys) == 2:
        spread = yields[keys[0]] - yields[keys[1]]
    return {"yields": yields, "spread": spread, "source": "investing.com"}

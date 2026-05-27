"""Sovereign 2Y yield scraper for macro anchors."""

from __future__ import annotations

import logging
import re
from typing import Optional

import httpx

from aaim_terminal.scrapers.http_utils import INVESTING_HEADERS, async_client

logger = logging.getLogger(__name__)

# Primary URLs first; alternates handle Investing.com slug changes.
YIELD_URLS: dict[str, list[str]] = {
    "DE02Y": [
        "https://www.investing.com/rates-bonds/germany-2-year-bond-yield",
    ],
    "US02Y": [
        "https://www.investing.com/rates-bonds/u.s.-2-year-bond-yield",
        "https://www.investing.com/rates-bonds/united-states-2-year-bond-yield",
    ],
    "GB02Y": [
        "https://www.investing.com/rates-bonds/u.k.-2-year-bond-yield",
        "https://www.investing.com/rates-bonds/united-kingdom-2-year-bond-yield",
    ],
    "CH02Y": [
        "https://www.investing.com/rates-bonds/switzerland-2-year-bond-yield",
    ],
    "AU02Y": [
        "https://www.investing.com/rates-bonds/australia-2-year-bond-yield",
    ],
}

FALLBACK_YIELDS = {
    "DE02Y": 2.45,
    "US02Y": 4.03,
    "GB02Y": 4.12,
    "CH02Y": 1.05,
    "AU02Y": 4.02,
}

YAHOO_YIELD_SYMBOLS = {
    "DE02Y": "DE2YT=RR",
    "US02Y": "^UST2Y",
    "GB02Y": "GB2YT=RR",
    "CH02Y": "CH2YT=RR",
    "AU02Y": "AU2YT=RR",
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

_PRICE_PATTERNS = [
    re.compile(r'data-test="instrument-price-last"[^>]*>([\d.]+)'),
    re.compile(r'class="[^"]*text-5xl[^"]*"[^>]*>([\d.]+)'),
    re.compile(r'"last_last":\s*"([\d.]+)"'),
    re.compile(r'"last":\s*([\d.]+)'),
]


def _parse_yield(html: str) -> Optional[float]:
    for pattern in _PRICE_PATTERNS:
        match = pattern.search(html)
        if match:
            value = float(match.group(1))
            if 0 < value < 30:
                return value
    return None


async def _fetch_yahoo_yield(key: str) -> Optional[float]:
    symbol = YAHOO_YIELD_SYMBOLS.get(key)
    if not symbol:
        return None
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    try:
        async with async_client() as client:
            resp = await client.get(url, params={"interval": "1d", "range": "1d"})
            resp.raise_for_status()
            price = resp.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
            if price and 0 < float(price) < 30:
                return float(price)
    except Exception as exc:
        logger.debug("Yahoo yield failed for %s: %s", key, exc)
    return None


async def _scrape_yield(key: str) -> tuple[float, str]:
    urls = YIELD_URLS.get(key, [])
    async with async_client() as client:
        for url in urls:
            try:
                resp = await client.get(url, headers=INVESTING_HEADERS)
                if resp.status_code == 404:
                    continue
                resp.raise_for_status()
                value = _parse_yield(resp.text)
                if value is not None:
                    return value, "investing.com"
            except httpx.HTTPError as exc:
                logger.debug("Yield URL failed for %s (%s): %s", key, url, exc)

    yahoo = await _fetch_yahoo_yield(key)
    if yahoo is not None:
        return yahoo, "yahoo.finance"

    logger.info("Using fallback yield for %s", key)
    return FALLBACK_YIELDS[key], "fallback"


async def fetch_macro_spread(symbol: str) -> dict:
    keys = PAIR_YIELD_MAP.get(symbol, [])
    yields: dict[str, float] = {}
    sources: list[str] = []

    for k in keys:
        value, source = await _scrape_yield(k)
        yields[k] = value
        sources.append(source)

    spread = None
    if len(keys) == 2:
        spread = yields[keys[0]] - yields[keys[1]]

    overall_source = "investing.com" if all(s == "investing.com" for s in sources) else "mixed"
    if all(s == "fallback" for s in sources):
        overall_source = "fallback"

    return {"yields": yields, "spread": spread, "source": overall_source}

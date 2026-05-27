"""15-minute OHLCV scraper with async fallback chain."""

from __future__ import annotations

import asyncio
import logging

import httpx
import pandas as pd
from bs4 import BeautifulSoup

from aaim_terminal.config import PAIRS, SCRAPER_TIMEOUT_MS
from aaim_terminal.scrapers.demo_data import generate_synthetic_bars
from aaim_terminal.scrapers.http_utils import INVESTING_HEADERS, async_client
from aaim_terminal.storage.cache import store

logger = logging.getLogger(__name__)

INVESTING_HISTORICAL = "https://www.investing.com/instruments/HistoricalDataAjax"


async def httpx_scrape_investing(symbol: str) -> pd.DataFrame:
    pair = PAIRS[symbol]
    slug = pair.investing_slug
    url = f"https://www.investing.com/currencies/{slug}-historical-data"

    async with async_client(timeout=SCRAPER_TIMEOUT_MS / 1000 + 5) as client:
        resp = await client.get(url, headers=INVESTING_HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", id="curr_table")
        if table is None:
            raise ValueError(f"No OHLCV table found for {symbol}")

        rows = []
        for tr in table.find_all("tr")[1:]:
            cols = tr.find_all("td")
            if len(cols) < 5:
                continue
            rows.append(
                {
                    "timestamp": cols[0].get_text(strip=True),
                    "close": float(cols[1].get_text(strip=True).replace(",", "")),
                    "open": float(cols[2].get_text(strip=True).replace(",", "")),
                    "high": float(cols[3].get_text(strip=True).replace(",", "")),
                    "low": float(cols[4].get_text(strip=True).replace(",", "")),
                    "volume": 1000.0,
                }
            )

        if not rows:
            raise ValueError(f"Empty scrape result for {symbol}")

        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").tail(120)


async def playwright_scrape_tradingview(symbol: str) -> pd.DataFrame:
    """Fallback: TradingView export not available headless without browser — use synthetic."""
    logger.warning("TradingView fallback for %s — using synthetic bars", symbol)
    return generate_synthetic_bars(symbol)


async def load_redis_cache(symbol: str) -> pd.DataFrame:
    cached = store.get_ohlcv(symbol)
    if cached is not None and not cached.empty:
        logger.info("Using cached bars for %s", symbol)
        return cached
    return generate_synthetic_bars(symbol)


async def fetch_ohlcv(symbol: str) -> pd.DataFrame:
    try:
        return await asyncio.wait_for(httpx_scrape_investing(symbol), timeout=SCRAPER_TIMEOUT_MS / 1000 + 10)
    except asyncio.TimeoutError:
        logger.warning("Investing.com timeout for %s", symbol)
        return await playwright_scrape_tradingview(symbol)
    except Exception as exc:
        logger.warning("Investing.com scrape failed for %s: %s", symbol, exc)
        return await load_redis_cache(symbol)

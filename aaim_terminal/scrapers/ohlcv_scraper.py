"""15-minute OHLCV scraper with async fallback chain."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup

from aaim_terminal.config import PAIRS, SCRAPER_TIMEOUT_MS
from aaim_terminal.scrapers.demo_data import generate_synthetic_bars
from aaim_terminal.scrapers.http_utils import INVESTING_HEADERS, async_client
from aaim_terminal.storage.cache import store

logger = logging.getLogger(__name__)

INVESTING_AJAX = "https://www.investing.com/instruments/HistoricalDataAjax"
MIN_BARS = 60  # engine lookback target


def _yahoo_symbol(symbol: str) -> str:
    return f"{symbol}=X"


def _parse_price(value: str) -> float:
    cleaned = value.strip().replace(",", "")
    if not cleaned or cleaned.endswith("%"):
        raise ValueError(f"Not a price: {value!r}")
    return float(cleaned)


def _parse_investing_table(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="curr_table")
    if table is None:
        raise ValueError("No curr_table in Investing.com response")

    header_cells = table.find("tr").find_all("th")
    headers = [cell.get_text(strip=True).lower() for cell in header_cells]

    def col_index(*names: str) -> Optional[int]:
        for name in names:
            for idx, header in enumerate(headers):
                if name in header:
                    return idx
        return None

    ts_idx = col_index("date")
    close_idx = col_index("price", "close", "last")
    open_idx = col_index("open")
    high_idx = col_index("high")
    low_idx = col_index("low")
    vol_idx = col_index("vol")

    if ts_idx is None or open_idx is None or high_idx is None or low_idx is None:
        raise ValueError(f"Unexpected Investing.com headers: {headers}")

    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = tr.find_all("td")
        if len(cols) <= max(ts_idx, open_idx, high_idx, low_idx):
            continue
        texts = [col.get_text(strip=True) for col in cols]
        try:
            close = _parse_price(texts[close_idx if close_idx is not None else open_idx])
            rows.append(
                {
                    "timestamp": texts[ts_idx],
                    "close": close,
                    "open": _parse_price(texts[open_idx]),
                    "high": _parse_price(texts[high_idx]),
                    "low": _parse_price(texts[low_idx]),
                    "volume": _parse_price(texts[vol_idx]) if vol_idx is not None and vol_idx < len(texts) else 1000.0,
                }
            )
        except (ValueError, IndexError):
            continue

    if not rows:
        raise ValueError("Empty Investing.com OHLCV table")

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    return df.sort_values("timestamp")


async def httpx_scrape_investing_ajax(symbol: str) -> pd.DataFrame:
    """Fetch 15m bars via Investing.com HistoricalDataAjax (session + POST)."""
    pair = PAIRS[symbol]
    curr_id = pair.investing_curr_id
    if curr_id is None:
        raise ValueError(f"No investing_curr_id for {symbol}")

    slug = pair.investing_slug
    page_url = f"https://www.investing.com/currencies/{slug}-historical-data"
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    payload = (
        f"curr_id={curr_id}"
        f"&sdate={start.strftime('%m/%d/%Y')}"
        f"&edate={end.strftime('%m/%d/%Y')}"
        f"&interval_sec=900"
        f"&lang_ID=1"
    )

    ajax_headers = {
        **INVESTING_HEADERS,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": page_url,
    }

    async with async_client(timeout=SCRAPER_TIMEOUT_MS / 1000 + 10) as client:
        page_resp = await client.get(page_url, headers=INVESTING_HEADERS)
        page_resp.raise_for_status()

        resp = None
        for attempt in range(3):
            resp = await client.post(INVESTING_AJAX, content=payload, headers=ajax_headers)
            if resp.status_code != 403:
                break
            await asyncio.sleep(0.75 * (attempt + 1))
            await client.get(page_url, headers=INVESTING_HEADERS)

        if resp is None:
            raise ValueError("No response from Investing.com AJAX")
        resp.raise_for_status()
        return _parse_investing_table(resp.text)


async def httpx_scrape_yahoo(symbol: str) -> pd.DataFrame:
    """Fetch 15m FX bars from Yahoo Finance chart API."""
    yahoo_sym = _yahoo_symbol(symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}"
    params = {"interval": "15m", "range": "5d"}

    async with async_client(timeout=SCRAPER_TIMEOUT_MS / 1000 + 10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        result = resp.json()["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]

        rows = []
        for i, ts in enumerate(timestamps):
            o, h, l, c = quote["open"][i], quote["high"][i], quote["low"][i], quote["close"][i]
            if o is None or h is None or l is None or c is None:
                continue
            vol = quote.get("volume", [None] * len(timestamps))[i] or 0
            rows.append(
                {
                    "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc),
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                    "volume": float(vol),
                }
            )

        if not rows:
            raise ValueError(f"Empty Yahoo Finance result for {symbol}")

        df = pd.DataFrame(rows)
        return df.sort_values("timestamp").tail(120)


async def load_redis_cache(symbol: str) -> pd.DataFrame:
    cached = store.get_ohlcv(symbol)
    if cached is not None and not cached.empty:
        logger.info("Using cached bars for %s", symbol)
        return cached
    return generate_synthetic_bars(symbol)


async def fetch_ohlcv(symbol: str) -> tuple[pd.DataFrame, str]:
    """Returns (bars, source_label)."""
    investing_df: Optional[pd.DataFrame] = None
    yahoo_df: Optional[pd.DataFrame] = None

    try:
        investing_df = await asyncio.wait_for(
            httpx_scrape_investing_ajax(symbol),
            timeout=SCRAPER_TIMEOUT_MS / 1000 + 10,
        )
        if len(investing_df) >= MIN_BARS:
            return investing_df.tail(120), "investing.com"
        logger.info(
            "Investing.com returned %d bars for %s (need %d) — supplementing with Yahoo",
            len(investing_df),
            symbol,
            MIN_BARS,
        )
    except asyncio.TimeoutError:
        logger.warning("Investing.com timeout for %s", symbol)
    except Exception as exc:
        logger.warning("Investing.com scrape failed for %s: %s", symbol, exc)

    try:
        yahoo_df = await asyncio.wait_for(
            httpx_scrape_yahoo(symbol),
            timeout=SCRAPER_TIMEOUT_MS / 1000 + 10,
        )
        if investing_df is not None and not investing_df.empty:
            # Merge: prefer Yahoo depth, back-fill earliest slice from Investing if newer
            combined = pd.concat([investing_df, yahoo_df]).drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
            return combined.tail(120), "investing.com+yahoo"
        return yahoo_df, "yahoo.finance"
    except Exception as exc:
        logger.warning("Yahoo Finance scrape failed for %s: %s", symbol, exc)

    if investing_df is not None and not investing_df.empty:
        return investing_df, "investing.com"

    cached = await load_redis_cache(symbol)
    source = "cache" if store.get_ohlcv(symbol) is not None else "synthetic"
    return cached, source

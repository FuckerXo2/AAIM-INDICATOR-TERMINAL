"""Background scraper orchestration."""

from __future__ import annotations

import asyncio
import logging

from aaim_terminal.config import FUTURES_REFRESH_SECONDS, OHLCV_REFRESH_SECONDS, OHLCV_STAGGER_SECONDS, PAIRS
from aaim_terminal.scrapers.cftc_scraper import fetch_cot_positions
from aaim_terminal.scrapers.futures_scraper import fetch_pair_futures_proxy
from aaim_terminal.scrapers.ohlcv_scraper import fetch_ohlcv
from aaim_terminal.scrapers.yield_scraper import fetch_macro_spread
from aaim_terminal.storage.cache import store

logger = logging.getLogger(__name__)

_running = False


async def refresh_pair_ohlcv(symbol: str) -> None:
    try:
        bars, source = await fetch_ohlcv(symbol)
        if bars is not None and not bars.empty:
            await store.set_ohlcv(symbol, bars, source=source)
        else:
            store.set_scraper_status(symbol, "ohlcv", "empty")
    except Exception as exc:
        logger.error("OHLCV refresh failed for %s: %s", symbol, exc)
        store.set_scraper_status(symbol, "ohlcv", "error")


async def refresh_pair_auxiliary(symbol: str) -> None:
    try:
        futures = await fetch_pair_futures_proxy(symbol)
        store.set_futures(symbol, futures)
        store.set_scraper_status(symbol, "futures", futures.get("source", "ok"))
        macro = await fetch_macro_spread(symbol)
        store.set_macro(symbol, macro)
        store.set_scraper_status(symbol, "yield_scraper", macro.get("source", "ok"))
    except Exception as exc:
        logger.error("Auxiliary refresh failed for %s: %s", symbol, exc)
        store.set_scraper_status(symbol, "futures", "error")
        store.set_scraper_status(symbol, "yield_scraper", "error")


async def refresh_cot() -> None:
    while _running:
        try:
            cot = await fetch_cot_positions()
            store.set_cot(cot)
            logger.info("CFTC COT positions refreshed")
        except Exception as exc:
            logger.error("COT refresh failed: %s", exc)
        await asyncio.sleep(3600 * 6)


async def ohlcv_worker(symbol: str, stagger_index: int) -> None:
    await asyncio.sleep(stagger_index * OHLCV_STAGGER_SECONDS)
    while _running:
        await refresh_pair_ohlcv(symbol)
        await asyncio.sleep(OHLCV_REFRESH_SECONDS)


async def futures_worker(symbol: str) -> None:
    while _running:
        await refresh_pair_auxiliary(symbol)
        await asyncio.sleep(FUTURES_REFRESH_SECONDS)


async def start_scraper_workers() -> None:
    global _running
    _running = True
    tasks = [asyncio.create_task(refresh_cot())]
    for i, symbol in enumerate(PAIRS):
        tasks.append(asyncio.create_task(ohlcv_worker(symbol, i)))
        tasks.append(asyncio.create_task(futures_worker(symbol)))
    logger.info("Started scraper workers for %d pairs", len(PAIRS))
    await asyncio.gather(*tasks)


async def stop_scraper_workers() -> None:
    global _running
    _running = False


async def bootstrap_data() -> None:
    """Seed all pairs with initial data on startup."""
    from aaim_terminal.scrapers.demo_data import generate_synthetic_bars

    for symbol in PAIRS:
        bars = generate_synthetic_bars(symbol)
        await store.set_ohlcv(symbol, bars, source="bootstrap")
        store.set_scraper_status(symbol, "ohlcv", "bootstrap")
        store.set_scraper_status(symbol, "futures", "pending")
        store.set_scraper_status(symbol, "yield_scraper", "pending")

    try:
        store.set_cot(await fetch_cot_positions())
    except Exception:
        store.set_cot({})

    refresh_tasks = [refresh_pair_ohlcv(s) for s in PAIRS] + [refresh_pair_auxiliary(s) for s in PAIRS]
    await asyncio.gather(*refresh_tasks, return_exceptions=True)

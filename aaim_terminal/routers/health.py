"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from aaim_terminal.config import MAX_BAR_AGE_SECONDS, PAIRS
from aaim_terminal.models import HealthResponse, ScraperStatus
from aaim_terminal.storage.cache import store

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    statuses: list[ScraperStatus] = []
    degraded = False

    for symbol in PAIRS:
        scraper = store.get_scraper_status(symbol)
        age = store.last_bar_age_seconds(symbol)
        ohlcv_status = scraper.get("ohlcv", "unknown")

        if age is not None and age > MAX_BAR_AGE_SECONDS:
            ohlcv_status = "stale"
            degraded = True
        if ohlcv_status in ("error", "unknown", "stale"):
            degraded = True

        statuses.append(
            ScraperStatus(
                symbol=symbol,
                ohlcv=ohlcv_status,
                last_bar_age_seconds=round(age, 1) if age is not None else None,
                futures=scraper.get("futures", "unknown"),
                yield_scraper=scraper.get("yield_scraper", "unknown"),
            )
        )

    return HealthResponse(
        status="degraded" if degraded else "ok",
        scrapers=statuses,
        pairs_monitored=len(PAIRS),
    )

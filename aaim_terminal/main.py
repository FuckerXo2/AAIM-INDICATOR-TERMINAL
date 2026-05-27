"""FastAPI application entry point for AAIM Indicator Terminal V8.3."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aaim_terminal import __version__
from aaim_terminal.config import PAIRS
from aaim_terminal.routers import desk, health, pairs, stream
from aaim_terminal.scrapers.worker import bootstrap_data, start_scraper_workers, stop_scraper_workers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

_scraper_task: Optional[asyncio.Task] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scraper_task
    logger.info("AAIM Terminal V%s starting — 8-pair universe", __version__)
    await bootstrap_data()
    _scraper_task = asyncio.create_task(start_scraper_workers())
    yield
    await stop_scraper_workers()
    if _scraper_task:
        _scraper_task.cancel()
        try:
            await _scraper_task
        except asyncio.CancelledError:
            pass
    logger.info("AAIM Terminal shutdown complete")


app = FastAPI(
    title="AAIM Indicator Terminal",
    description="Aggregated Volume-Weighted Auction Market Tracer V8.3 — 8-Pair FastAPI Build",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(desk.router)
app.include_router(health.router)
app.include_router(pairs.router)
app.include_router(stream.router)


@app.get("/")
async def root():
    return {
        "service": "AAIM Indicator Terminal",
        "version": __version__,
        "pairs": list(PAIRS.keys()),
        "endpoints": {
            "health": "/health",
            "desk_overview": "/desk/overview",
            "desk_risk": "/desk/risk",
            "desk_sessions": "/desk/sessions",
            "desk_cot": "/desk/cot",
            "pairs": "/pairs",
            "forecast": "/pairs/{symbol}/forecast",
            "analytics": "/pairs/{symbol}/analytics",
            "bars": "/pairs/{symbol}/bars",
            "macro": "/pairs/{symbol}/macro",
            "futures": "/pairs/{symbol}/futures",
            "gantt": "/pairs/{symbol}/gantt",
            "pivots": "/pairs/{symbol}/pivots",
            "profile": "/pairs/{symbol}/profile",
            "entropy": "/pairs/{symbol}/entropy",
            "websocket": "/ws/live/{symbol}",
        },
    }

"""WebSocket live bar stream."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from aaim_terminal.config import VALID_SYMBOLS
from aaim_terminal.engine.basilica import generate_forecast
from aaim_terminal.scrapers.demo_data import generate_synthetic_bars
from aaim_terminal.storage.cache import store

router = APIRouter(tags=["stream"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/live/{symbol}")
async def live_stream(websocket: WebSocket, symbol: str) -> None:
    sym = symbol.upper()
    if sym not in VALID_SYMBOLS:
        await websocket.close(code=4404, reason=f"Unknown pair: {symbol}")
        return

    await websocket.accept()
    try:
        while True:
            bars = store.get_ohlcv(sym)
            if bars is None or bars.empty:
                bars = generate_synthetic_bars(sym)

            forecast = generate_forecast(sym, bars)
            last_bar = bars.iloc[-1]
            payload = {
                "type": "bar_close",
                "symbol": sym,
                "bar": {
                    "timestamp": str(last_bar["timestamp"]),
                    "open": float(last_bar["open"]),
                    "high": float(last_bar["high"]),
                    "low": float(last_bar["low"]),
                    "close": float(last_bar["close"]),
                    "volume": float(last_bar.get("volume", 0)),
                },
                "forecast": json.loads(forecast.model_dump_json()),
            }
            await websocket.send_json(payload)
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for %s", sym)
    except Exception as exc:
        logger.error("WebSocket error for %s: %s", sym, exc)
        await websocket.close(code=1011)

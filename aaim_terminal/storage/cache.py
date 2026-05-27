"""In-memory cache with optional Redis backing and SQLite persistence."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "aaim_cache.db"


class StateStore:
    def __init__(self) -> None:
        self._ohlcv: dict[str, pd.DataFrame] = {}
        self._last_fetch: dict[str, datetime] = {}
        self._scraper_status: dict[str, dict[str, str]] = {}
        self._macro: dict[str, dict] = {}
        self._futures: dict[str, dict] = {}
        self._cot: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ohlcv_cache (
                    symbol TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    open REAL, high REAL, low REAL, close REAL, volume REAL,
                    PRIMARY KEY (symbol, timestamp)
                )
                """
            )
            conn.commit()

    async def set_ohlcv(self, symbol: str, bars: pd.DataFrame, source: str = "live") -> None:
        async with self._lock:
            self._ohlcv[symbol] = bars.copy()
            self._last_fetch[symbol] = datetime.now(timezone.utc)
            self._scraper_status.setdefault(symbol, {})["ohlcv"] = source
            await asyncio.to_thread(self._persist_bars, symbol, bars)

    def _persist_bars(self, symbol: str, bars: pd.DataFrame) -> None:
        with sqlite3.connect(DB_PATH) as conn:
            for _, row in bars.iterrows():
                ts = row["timestamp"]
                if hasattr(ts, "isoformat"):
                    ts_str = ts.isoformat()
                else:
                    ts_str = str(ts)
                conn.execute(
                    """
                    INSERT OR REPLACE INTO ohlcv_cache
                    (symbol, timestamp, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        symbol,
                        ts_str,
                        float(row["open"]),
                        float(row["high"]),
                        float(row["low"]),
                        float(row["close"]),
                        float(row.get("volume", 0)),
                    ),
                )
            conn.commit()

    def get_ohlcv(self, symbol: str) -> Optional[pd.DataFrame]:
        cached = self._ohlcv.get(symbol)
        if cached is not None and not cached.empty:
            return cached.copy()
        return self._load_from_sqlite(symbol)

    def _load_from_sqlite(self, symbol: str) -> Optional[pd.DataFrame]:
        if not DB_PATH.exists():
            return None
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(
                "SELECT timestamp, open, high, low, close, volume FROM ohlcv_cache WHERE symbol = ? ORDER BY timestamp",
                conn,
                params=(symbol,),
            )
        if df.empty:
            return None
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df

    def last_bar_age_seconds(self, symbol: str) -> Optional[float]:
        last = self._last_fetch.get(symbol)
        if last is None:
            bars = self.get_ohlcv(symbol)
            if bars is None or bars.empty:
                return None
            last_ts = pd.to_datetime(bars["timestamp"].iloc[-1], utc=True)
            return (datetime.now(timezone.utc) - last_ts.to_pydatetime()).total_seconds()
        return (datetime.now(timezone.utc) - last).total_seconds()

    def set_scraper_status(self, symbol: str, component: str, status: str) -> None:
        self._scraper_status.setdefault(symbol, {})[component] = status

    def get_scraper_status(self, symbol: str) -> dict[str, str]:
        return self._scraper_status.get(symbol, {"ohlcv": "unknown", "futures": "unknown", "yield_scraper": "unknown"})

    def set_macro(self, symbol: str, data: dict) -> None:
        self._macro[symbol] = data

    def get_macro(self, symbol: str) -> Optional[dict]:
        return self._macro.get(symbol)

    def set_futures(self, symbol: str, data: dict) -> None:
        self._futures[symbol] = data

    def get_futures(self, symbol: str) -> Optional[dict]:
        return self._futures.get(symbol)

    def set_cot(self, data: dict) -> None:
        self._cot = data

    def get_cot(self) -> dict:
        return self._cot


store = StateStore()

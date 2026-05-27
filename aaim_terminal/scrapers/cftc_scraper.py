"""CFTC COT positioning scraper."""

from __future__ import annotations

import io
import logging
import zipfile
from datetime import datetime, timezone

import httpx
import pandas as pd

from aaim_terminal.config import PAIRS

logger = logging.getLogger(__name__)

CFTC_ZIP_URL = "https://www.cftc.gov/dea/newcot/deahistfo.zip"

CFTC_CODES = {
    "099741": "EUR",
    "096742": "GBP",
    "112741": "AUD",
}


async def fetch_cot_positions() -> dict[str, dict]:
    headers = {"User-Agent": "Mozilla/5.0"}
    result: dict[str, dict] = {}
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(CFTC_ZIP_URL, headers=headers)
            resp.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                csv_name = next(n for n in zf.namelist() if n.endswith(".txt") or n.endswith(".csv"))
                with zf.open(csv_name) as f:
                    df = pd.read_csv(f, low_memory=False)

            for code, label in CFTC_CODES.items():
                mask = df.iloc[:, 0].astype(str).str.contains(code, na=False)
                subset = df[mask]
                if subset.empty:
                    result[label] = {"net_long": 0, "net_short": 0, "source": "fallback"}
                    continue
                row = subset.iloc[-1]
                result[label] = {
                    "net_long": float(row.get("NonComm_Positions_Long_All", 0) or 0),
                    "net_short": float(row.get("NonComm_Positions_Short_All", 0) or 0),
                    "source": "cftc.gov",
                    "as_of": str(row.iloc[2]) if len(row) > 2 else None,
                }
    except Exception as exc:
        logger.warning("CFTC scrape failed: %s", exc)
        for label in CFTC_CODES.values():
            result[label] = {"net_long": 0, "net_short": 0, "source": "fallback"}

    return result


def cftc_code_for_symbol(symbol: str) -> Optional[str]:
    return PAIRS[symbol].cftc_code

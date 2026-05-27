"""CFTC COT positioning scraper."""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from datetime import datetime, timezone
from typing import Optional

import httpx

from aaim_terminal.config import PAIRS
from aaim_terminal.scrapers.http_utils import async_client

logger = logging.getLogger(__name__)

# Current weekly disaggregated comma-delimited file (updated each Tuesday)
CFTC_CURRENT_URL = "https://www.cftc.gov/dea/newcot/deacom.txt"

# Yearly archives — try current and previous year
CFTC_ARCHIVE_URLS = [
    "https://www.cftc.gov/files/dea/history/deafut_26.zip",
    "https://www.cftc.gov/files/dea/history/deafut_25.zip",
]

CFTC_CODES = {
    "099741": "EUR",
    "096742": "GBP",
    "112741": "AUD",
}


def _parse_cot_row(row: list[str], label: str) -> dict:
    """Extract leveraged-funds positioning from a disaggregated COT row."""
    try:
        # Disaggregated format: managed money long ~ col 15, short ~ col 16 (0-indexed varies)
        long_idx, short_idx = 15, 16
        if len(row) > short_idx:
            net_long = float(row[long_idx].strip().replace(",", "") or 0)
            net_short = float(row[short_idx].strip().replace(",", "") or 0)
            as_of = row[2] if len(row) > 2 else None
            return {
                "net_long": net_long,
                "net_short": net_short,
                "source": "cftc.gov",
                "as_of": as_of,
            }
    except (ValueError, IndexError):
        pass
    return {"net_long": 0, "net_short": 0, "source": "fallback", "as_of": None}


def _parse_deacom_text(content: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    reader = csv.reader(io.StringIO(content))
    for row in reader:
        if not row:
            continue
        row_text = ",".join(row)
        for code, label in CFTC_CODES.items():
            if code in row_text and label not in result:
                result[label] = _parse_cot_row(row, label)
    return result


async def _fetch_current_cot() -> Optional[dict[str, dict]]:
    try:
        async with async_client(timeout=30.0) as client:
            resp = await client.get(CFTC_CURRENT_URL)
            resp.raise_for_status()
            parsed = _parse_deacom_text(resp.text)
            if parsed:
                return parsed
    except Exception as exc:
        logger.debug("CFTC current file failed: %s", exc)
    return None


async def _fetch_archive_cot() -> Optional[dict[str, dict]]:
    async with async_client(timeout=45.0) as client:
        for url in CFTC_ARCHIVE_URLS:
            try:
                resp = await client.get(url)
                if resp.status_code == 404:
                    continue
                resp.raise_for_status()
                with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                    csv_name = next(
                        (n for n in zf.namelist() if n.endswith(".txt") or n.endswith(".csv")),
                        None,
                    )
                    if not csv_name:
                        continue
                    with zf.open(csv_name) as f:
                        content = f.read().decode("utf-8", errors="ignore")
                parsed = _parse_deacom_text(content)
                if parsed:
                    return parsed
            except Exception as exc:
                logger.debug("CFTC archive failed (%s): %s", url, exc)
    return None


async def fetch_cot_positions() -> dict[str, dict]:
    result = await _fetch_current_cot()
    if not result:
        result = await _fetch_archive_cot()

    if result:
        logger.info("CFTC COT loaded for: %s", ", ".join(result.keys()))
        return result

    logger.info("CFTC unavailable — using fallback positioning")
    return {
        label: {"net_long": 0, "net_short": 0, "source": "fallback", "as_of": None}
        for label in CFTC_CODES.values()
    }


def cftc_code_for_symbol(symbol: str) -> Optional[str]:
    return PAIRS[symbol].cftc_code

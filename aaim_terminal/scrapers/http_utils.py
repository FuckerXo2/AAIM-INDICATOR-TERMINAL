"""Shared HTTP client settings for scrapers."""

from __future__ import annotations

import httpx

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

INVESTING_HEADERS = {
    **BROWSER_HEADERS,
    "Referer": "https://www.investing.com/",
    "Domain": "www.investing.com",
}


def async_client(timeout: float = 15.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=BROWSER_HEADERS)

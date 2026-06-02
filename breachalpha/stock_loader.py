"""Stock data loader with multi-source fallback.

Uses DataFetcher for automatic fallback across:
- yfinance (primary)
- Alpha Vantage (official API)
- NSE India (Indian stocks)
- Yahoo Finance scraping (fallback)

Maintains backward compatibility with existing code.
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from .data_sources import DataFetcher, CACHE_DIR, get_fetcher

logger = logging.getLogger(__name__)

MARKET_INDEX = "^GSPC"


def _get_fetcher(alpha_vantage_key: str = "") -> DataFetcher:
    """Get the configured data fetcher."""
    return get_fetcher(alpha_vantage_key)


def fetch_stock_data(
    ticker: str,
    start: str | pd.Timestamp = "2010-01-01",
    end: str | pd.Timestamp | None = None,
    force_refresh: bool = False,
    source: str = "",
    alpha_vantage_key: str = "",
) -> pd.DataFrame:
    """Fetch historical stock data for a single ticker.

    Uses multi-source fetcher with automatic fallback.
    """
    fetcher = _get_fetcher(alpha_vantage_key)

    if source:
        # Use specific source
        source_obj = fetcher.sources.get(source)
        if source_obj:
            return source_obj.fetch(ticker, start, end)
        logger.warning("Unknown source: %s, using default fallback", source)

    return fetcher.fetch(ticker, start, end, force_refresh)


def fetch_stock_batch(
    tickers: list[str],
    start: str | pd.Timestamp = "2010-01-01",
    end: str | pd.Timestamp | None = None,
    force_refresh: bool = False,
    alpha_vantage_key: str = "",
) -> dict[str, pd.DataFrame]:
    """Fetch stock data for multiple tickers."""
    fetcher = _get_fetcher(alpha_vantage_key)
    return fetcher.fetch_batch(tickers, start, end)


def fetch_market_data(
    start: str | pd.Timestamp = "2010-01-01",
    end: str | pd.Timestamp | None = None,
    force_refresh: bool = False,
    benchmark: str = MARKET_INDEX,
    alpha_vantage_key: str = "",
) -> pd.DataFrame:
    """Fetch market benchmark data."""
    fetcher = _get_fetcher(alpha_vantage_key)
    return fetcher.fetch_market(benchmark, start, end)


def clear_cache(older_than_days: Optional[int] = None) -> int:
    """Clear cached stock data. Returns number of files removed."""
    fetcher = _get_fetcher()
    hours = older_than_days * 24 if older_than_days is not None else None
    return fetcher.clear_cache(hours)


def get_cache_info() -> dict:
    """Return info about cached stock data."""
    if not CACHE_DIR.exists():
        return {"cached_files": 0, "total_size_kb": 0, "tickers": []}

    files = list(CACHE_DIR.glob("*.csv"))
    total_size = sum(f.stat().st_size for f in files)
    tickers = sorted(set(f.stem.split("_")[0] for f in files))

    return {
        "cached_files": len(files),
        "total_size_kb": round(total_size / 1024, 1),
        "tickers": tickers,
    }


def get_data_sources_status() -> dict:
    """Get status of all available data sources."""
    fetcher = _get_fetcher()
    return fetcher.get_source_status()

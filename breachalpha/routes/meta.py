"""Health, demo, config presets, cache, data-sources endpoints."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, Request

from ..schemas import (
    HealthResponse, DemoCase, CacheInfoResponse, ConfigPreset,
    AnalysisConfigRequest, DataSourceConfigResponse, DataSourceStatus,
    DataSourceConfigRequest,
)
from ..model import load_model
from ..stock_loader import (
    fetch_stock_data, fetch_market_data,
    get_cache_info, clear_cache, get_data_sources_status,
)
from ..feature_engine import BreachEvent, compute_features
from ..services.model import get_or_train_model, predict_severity
import pandas as pd


def create_meta_routes(limiter) -> APIRouter:
    router = APIRouter()

    @router.get("/api/health", response_model=HealthResponse)
    @limiter.exempt
    async def health_check(request: Request):
        model = load_model()
        return HealthResponse(
            status="ok",
            model_loaded=model is not None,
            version="0.1.0",
        )

    @router.get("/api/demo", response_model=list[DemoCase])
    @limiter.limit("30/minute")
    async def run_demo(request: Request):
        import asyncio
        import structlog
        log = structlog.get_logger(__name__)

        demo_cases = [
            DemoCase(
                company="Equifax", ticker="EFX", breach_date="2017-09-07",
                pwn_count=147_000_000, breach_type="data_leak",
                description="Massive credit data breach exposing SSNs, birth dates, addresses",
            ),
            DemoCase(
                company="Capital One", ticker="COF", breach_date="2019-07-29",
                pwn_count=106_000_000, breach_type="data_leak",
                description="Cloud misconfiguration exposed credit card applications",
            ),
            DemoCase(
                company="Marriott", ticker="MAR", breach_date="2018-11-30",
                pwn_count=500_000_000, breach_type="data_leak",
                description="Starwood reservation system breach (4 years undetected)",
            ),
        ]

        market_data = fetch_market_data(start="2015-01-01")
        model = get_or_train_model()

        for case in demo_cases:
            try:
                stock_data = fetch_stock_data(case.ticker, start="2015-01-01")
                if stock_data.empty:
                    continue

                event = BreachEvent(
                    company_name=case.company, ticker=case.ticker,
                    breach_date=pd.Timestamp(case.breach_date),
                    pwn_count=case.pwn_count, breach_type=case.breach_type,
                    stock_data=stock_data, market_data=market_data,
                )

                features = await asyncio.to_thread(compute_features, event)
                if features is not None:
                    features_df = pd.DataFrame([features.to_dict()])
                    pred = predict_severity(model, features_df)
                    case.risk_score = pred["risk_score"]
                    case.prediction = pred["prediction"]
                    case.confidence = pred["confidence"]
            except Exception as e:
                log.error("demo_failed", company=case.company, error=str(e))

        return demo_cases

    @router.get("/api/config/presets", response_model=list[ConfigPreset])
    @limiter.exempt
    async def get_config_presets(request: Request):
        return [
            ConfigPreset(
                name="fast",
                description="Quick analysis — minimal windows, fastest computation",
                config=AnalysisConfigRequest(
                    estimation_window=100, pre_event_window=10, post_event_window=20,
                    recovery_max_days=30, car_long_end=15,
                ),
            ),
            ConfigPreset(
                name="standard",
                description="Balanced analysis — good accuracy with reasonable speed",
                config=AnalysisConfigRequest(),
            ),
            ConfigPreset(
                name="thorough",
                description="Deep analysis — maximum accuracy, slower computation",
                config=AnalysisConfigRequest(
                    estimation_window=500, pre_event_window=60, post_event_window=120,
                    recovery_max_days=180, car_long_end=60,
                ),
            ),
            ConfigPreset(
                name="conservative",
                description="Conservative thresholds — only flags clearly severe breaches",
                config=AnalysisConfigRequest(
                    threshold_critical=-0.20, threshold_high=-0.10, threshold_medium=-0.05,
                ),
            ),
            ConfigPreset(
                name="sensitive",
                description="Sensitive thresholds — catches milder impacts",
                config=AnalysisConfigRequest(
                    threshold_critical=-0.10, threshold_high=-0.05, threshold_medium=-0.01,
                ),
            ),
        ]

    @router.get("/api/cache", response_model=CacheInfoResponse)
    @limiter.exempt
    async def get_cache_info_endpoint(request: Request):
        info = get_cache_info()
        return CacheInfoResponse(**info)

    @router.delete("/api/cache")
    @limiter.exempt
    async def clear_cache_endpoint(request: Request, older_than_days: int = None):
        count = clear_cache(older_than_days)
        return {"status": "ok", "cleared": count}

    @router.get("/api/data-sources", response_model=DataSourceConfigResponse)
    @limiter.exempt
    async def get_data_sources(request: Request):
        status = get_data_sources_status()
        sources = {name: DataSourceStatus(**info) for name, info in status.items()}
        return DataSourceConfigResponse(
            primary_source="yfinance",
            alpha_vantage_key_set=bool(os.environ.get("ALPHA_VANTAGE_API_KEY")),
            enable_fallback=True,
            cache_ttl_hours=24,
            sources=sources,
        )

    @router.get("/api/data-sources/test/{source_name}")
    @limiter.limit("10/minute")
    async def test_data_source(request: Request, source_name: str, ticker: str = "MSFT"):
        import asyncio
        import time as _time
        from ..data_sources import (
            YFinanceSource, AlphaVantageSource, NSEIndiaSource,
            YahooFinanceScrapeSource, DataFetcher, FetcherConfig,
        )
        from ..ticker_resolver import resolve_ticker

        resolved = resolve_ticker(ticker)
        if resolved and resolved != ticker:
            ticker = resolved

        if source_name == "auto":
            fetcher = DataFetcher(FetcherConfig(
                alpha_vantage_key=os.environ.get("ALPHA_VANTAGE_API_KEY", ""),
            ))
            start_time = _time.time()
            try:
                df = await asyncio.to_thread(fetcher.fetch, ticker, start="2024-01-01")
            except Exception as e:
                return {
                    "source": "auto (fallback chain)", "ticker": ticker,
                    "success": False, "error": str(e),
                }
            elapsed = _time.time() - start_time

            result = {
                "source": "auto (fallback chain)", "ticker": ticker,
                "success": not df.empty, "rows": len(df),
                "elapsed_seconds": round(elapsed, 2),
                "date_range": [
                    str(df.index.min())[:10] if not df.empty else None,
                    str(df.index.max())[:10] if not df.empty else None,
                ],
                "latest_close": float(df["Close"].iloc[-1]) if not df.empty and "Close" in df.columns else None,
            }
            if df.empty:
                result["error"] = (
                    "All data sources returned no data. "
                    "Yahoo Finance may be blocking requests — try installing curl_cffi: pip install curl_cffi"
                )
            return result

        sources = {
            "yfinance": YFinanceSource(),
            "alphavantage": AlphaVantageSource(os.environ.get("ALPHA_VANTAGE_API_KEY", "")),
            "nse_india": NSEIndiaSource(),
            "yahoo_scrape": YahooFinanceScrapeSource(),
        }

        source = sources.get(source_name)
        if not source:
            raise HTTPException(status_code=400, detail=f"Unknown source: {source_name}. Use 'auto' for fallback chain.")

        if not source.supports_ticker(ticker):
            raise HTTPException(status_code=400, detail=f"Source {source_name} does not support ticker {ticker}")

        try:
            start_time = _time.time()
            df = await asyncio.to_thread(source.fetch, ticker, start="2024-01-01")
            elapsed = _time.time() - start_time

            return {
                "source": source_name, "ticker": ticker,
                "success": not df.empty, "rows": len(df),
                "elapsed_seconds": round(elapsed, 2),
                "date_range": [
                    str(df.index.min())[:10] if not df.empty else None,
                    str(df.index.max())[:10] if not df.empty else None,
                ],
                "latest_close": float(df["Close"].iloc[-1]) if not df.empty and "Close" in df.columns else None,
            }
        except Exception as e:
            return {
                "source": source_name, "ticker": ticker,
                "success": False, "error": str(e),
            }

    return router

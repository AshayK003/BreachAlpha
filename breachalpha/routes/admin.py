"""Admin endpoints: train, data-sources configure."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from ..schemas import (
    TrainRequest, TrainResponse, DataSourceConfigRequest,
    DataSourceConfigResponse, DataSourceStatus,
)
from ..feature_engine import BreachEvent, compute_features
from ..model import train_model, save_model
from ..stock_loader import fetch_stock_data, fetch_market_data
from ..data_sources import DataFetcher, FetcherConfig


def create_admin_routes(limiter) -> APIRouter:
    router = APIRouter()

    @router.post("/api/train", response_model=TrainResponse)
    @limiter.limit("1/minute")
    async def train_model_endpoint(request: Request, req: TrainRequest):
        import asyncio

        path = Path(req.data_path).resolve()

        allowed_dirs = [
            (Path(__file__).parent.parent.parent / "data").resolve(),
            (Path(__file__).parent.parent.parent).resolve(),
        ]
        if not any(path.is_relative_to(d) for d in allowed_dirs):
            raise HTTPException(status_code=403, detail="Access denied: path outside allowed directories")

        if not path.exists():
            raise HTTPException(status_code=404, detail="Data file not found")

        def _train_worker():
            from ..breach_loader import load_breaches
            from ..ticker_resolver import resolve_all, load_overrides

            breaches = load_breaches(path)
            overrides = load_overrides()
            resolutions = resolve_all(breaches["Name"].tolist(), overrides)

            resolved = breaches[breaches["Name"].map(resolutions).notna()].copy()
            resolved["ticker"] = resolved["Name"].map(resolutions)

            if len(resolved) < 20:
                raise ValueError(f"Need at least 20 resolved companies to train (got {len(resolved)})")

            market_data = fetch_market_data(start="2010-01-01")
            features_list = []

            for _, row in resolved.iterrows():
                stock_data = fetch_stock_data(row["ticker"], start="2010-01-01")
                if stock_data.empty:
                    continue

                event = BreachEvent(
                    company_name=row["Name"], ticker=row["ticker"],
                    breach_date=row["BreachDate"], pwn_count=int(row["PwnCount"]),
                    breach_type="data_leak", stock_data=stock_data, market_data=market_data,
                )
                features = compute_features(event)
                if features is not None:
                    features_list.append(features.to_dict())

            if not features_list:
                raise ValueError("No features could be computed")

            df = pd.DataFrame(features_list)
            result = train_model(df)
            save_model(result["model"], result["metrics"])
            return result

        try:
            result = await asyncio.to_thread(_train_worker)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        return TrainResponse(
            status="ok",
            n_samples=result["metrics"]["n_samples"],
            cv_accuracy=result["metrics"]["cv_accuracy_mean"],
            cv_std=result["metrics"]["cv_accuracy_std"],
            feature_importance=result["metrics"]["feature_importance"],
        )

    @router.post("/api/data-sources/configure", response_model=DataSourceConfigResponse)
    @limiter.limit("10/minute")
    async def configure_data_sources(request: Request, req: DataSourceConfigRequest):
        if req.alpha_vantage_key:
            request.app.state.alpha_vantage_key = req.alpha_vantage_key

        current_key = getattr(request.app.state, "alpha_vantage_key", req.alpha_vantage_key or "")
        config = FetcherConfig(
            primary_source=req.primary_source,
            alpha_vantage_key=current_key,
            enable_fallback=req.enable_fallback,
            cache_ttl_hours=req.cache_ttl_hours,
        )
        fetcher = DataFetcher(config)

        status = fetcher.get_source_status()
        sources = {name: DataSourceStatus(**info) for name, info in status.items()}

        return DataSourceConfigResponse(
            primary_source=req.primary_source,
            alpha_vantage_key_set=bool(current_key),
            enable_fallback=req.enable_fallback,
            cache_ttl_hours=req.cache_ttl_hours,
            sources=sources,
        )

    return router

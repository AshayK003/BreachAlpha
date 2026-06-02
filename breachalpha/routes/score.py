"""Score endpoints: /api/score, /api/score/auto, /api/score/config."""

from __future__ import annotations

import asyncio

import pandas as pd
from fastapi import APIRouter, HTTPException, Request

from ..schemas import ScoreRequest, ScoreResponse, AutoScoreResponse, FeatureDetail, AnalysisConfigRequest
from ..feature_engine import (
    BreachEvent, compute_features, classify_severity,
    AnalysisConfig as FeatureConfig,
)
from ..ticker_resolver import resolve_ticker, detect_benchmark
from ..stock_loader import fetch_stock_data, fetch_market_data
from ..services.model import get_or_train_model, score_features
from ..services.scoring import (
    validate_ticker as _validate_ticker_svc,
    resolve_company_name_from_ticker,
    score_company as score_company_svc,
)


def _validate_ticker(ticker: str) -> str:
    try:
        return _validate_ticker_svc(ticker)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def create_score_routes(limiter) -> APIRouter:
    router = APIRouter()

    @router.post("/api/score", response_model=ScoreResponse)
    @limiter.limit("10/minute")
    async def score_company(request: Request, req: ScoreRequest):
        response, _ = await score_company_svc(
            company_name=req.company,
            breach_date=req.breach_date,
            records_affected=req.records_affected,
            breach_type=req.breach_type,
        )
        return response

    @router.post("/api/score/auto", response_model=AutoScoreResponse)
    @limiter.limit("5/minute")
    async def score_auto(request: Request, req: ScoreRequest):
        from ..breach_search import search_breach_incidents

        ticker = resolve_ticker(req.company)
        if ticker is None:
            raise HTTPException(status_code=404, detail=f"Could not resolve ticker for '{req.company}'")

        ticker = _validate_ticker(ticker)
        company_name = resolve_company_name_from_ticker(ticker)

        incidents = await asyncio.to_thread(search_breach_incidents, company_name, 5)
        breach_found = len(incidents) > 0

        if breach_found:
            top = max(incidents, key=lambda x: (x.records_affected, x.confidence))
            breach_date = top.date if top.date else req.breach_date
            records = top.records_affected if top.records_affected > 0 else req.records_affected
            breach_type = top.breach_type
            breach_confidence = top.confidence
        else:
            breach_date = req.breach_date
            records = req.records_affected
            breach_type = req.breach_type
            breach_confidence = 0.0

        benchmark = detect_benchmark(ticker)

        stock_data, market_data = await asyncio.gather(
            asyncio.to_thread(fetch_stock_data, ticker, "2015-01-01"),
            asyncio.to_thread(fetch_market_data, "2015-01-01", benchmark),
        )
        if stock_data.empty:
            raise HTTPException(status_code=404, detail=f"No stock data for {ticker}")

        event = BreachEvent(
            company_name=company_name, ticker=ticker,
            breach_date=pd.Timestamp(breach_date),
            pwn_count=records, breach_type=breach_type,
            stock_data=stock_data, market_data=market_data,
            benchmark=benchmark,
        )

        features = await asyncio.to_thread(compute_features, event)
        if features is None:
            raise HTTPException(
                status_code=422,
                detail=f"Insufficient data around breach date {breach_date} for {company_name}",
            )

        model = get_or_train_model()
        features_df = pd.DataFrame([features.to_dict()])
        prediction = score_features(model, features_df)

        return AutoScoreResponse(
            company=req.company, ticker=ticker,
            risk_score=prediction["risk_score"],
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
            probabilities=prediction["probabilities"],
            features=FeatureDetail.from_features(features, classify_severity(features.car_minus5_plus30)),
            breach_found=breach_found,
            breach_date_used=breach_date,
            records_used=records,
            breach_type_used=breach_type,
            breach_confidence=breach_confidence,
            incident_count=len(incidents),
        )

    @router.post("/api/score/config", response_model=ScoreResponse)
    @limiter.limit("10/minute")
    async def score_with_config(request: Request, req: ScoreRequest, config: AnalysisConfigRequest = None):
        if config is None:
            config = AnalysisConfigRequest()

        ticker = resolve_ticker(req.company)
        if ticker is None:
            raise HTTPException(status_code=404, detail=f"Could not resolve ticker for '{req.company}'")

        ticker = _validate_ticker(ticker)
        benchmark = detect_benchmark(ticker)

        stock_data, market_data = await asyncio.gather(
            asyncio.to_thread(fetch_stock_data, ticker, config.start_date),
            asyncio.to_thread(fetch_market_data, config.start_date, benchmark),
        )
        if stock_data.empty:
            raise HTTPException(status_code=404, detail=f"No stock data available for {ticker}")

        feature_config = FeatureConfig(
            estimation_window=config.estimation_window,
            pre_event_window=config.pre_event_window,
            post_event_window=config.post_event_window,
            recovery_max_days=config.recovery_max_days,
            threshold_critical=config.threshold_critical,
            threshold_high=config.threshold_high,
            threshold_medium=config.threshold_medium,
            car_short_start=config.car_short_start,
            car_short_end=config.car_short_end,
            car_long_start=config.car_long_start,
            car_long_end=config.car_long_end,
        )

        event = BreachEvent(
            company_name=req.company, ticker=ticker,
            breach_date=pd.Timestamp(req.breach_date),
            pwn_count=req.records_affected, breach_type=req.breach_type,
            stock_data=stock_data, market_data=market_data,
            benchmark=benchmark,
        )

        features = await asyncio.to_thread(compute_features, event, feature_config)
        if features is None:
            raise HTTPException(status_code=422, detail=f"Insufficient data for {req.company}")

        model = get_or_train_model()
        features_df = pd.DataFrame([features.to_dict()])
        prediction = score_features(model, features_df)

        return ScoreResponse(
            company=req.company, ticker=ticker,
            risk_score=prediction["risk_score"], prediction=prediction["prediction"],
            confidence=prediction["confidence"], probabilities=prediction["probabilities"],
            features=FeatureDetail.from_features(features, classify_severity(features.car_minus5_plus30, feature_config)),
        )

    return router

"""Explain endpoints: /api/explain, /api/explain/auto."""

from __future__ import annotations

import asyncio

import pandas as pd
from fastapi import APIRouter, Request

from ..schemas import (
    ExplainRequest, ExplainResponse, CalculationStepModel,
)
from ..feature_engine import (
    BreachEvent, compute_features,
)
from ..ticker_resolver import resolve_ticker, detect_benchmark
from ..stock_loader import fetch_stock_data, fetch_market_data
from ..explainability import generate_explanation
from ..services.model import get_or_train_model
from ..services.scoring import (
    validate_ticker,
    resolve_company_name_from_ticker,
)
from ..core.exceptions import TickerResolutionError, NoStockDataError, InsufficientDataError


def create_explain_routes(limiter) -> APIRouter:
    router = APIRouter()

    @router.post("/api/explain", response_model=ExplainResponse)
    @limiter.limit("10/minute")
    async def explain_score(request: Request, req: ExplainRequest):
        ticker = resolve_ticker(req.company)
        if ticker is None:
            raise TickerResolutionError(req.company)

        ticker = validate_ticker(ticker)
        benchmark = detect_benchmark(ticker)

        stock_data, market_data = await asyncio.gather(
            asyncio.to_thread(fetch_stock_data, ticker, "2015-01-01"),
            asyncio.to_thread(fetch_market_data, "2015-01-01", benchmark),
        )
        if stock_data.empty:
            raise NoStockDataError(ticker)

        event = BreachEvent(
            company_name=req.company, ticker=ticker,
            breach_date=pd.Timestamp(req.breach_date),
            pwn_count=req.records_affected, breach_type=req.breach_type,
            stock_data=stock_data, market_data=market_data,
            benchmark=benchmark,
        )

        features = await asyncio.to_thread(compute_features, event)
        if features is None:
            raise InsufficientDataError(req.company, req.breach_date)

        model = get_or_train_model()
        report = generate_explanation(event, features, model)

        return ExplainResponse(
            company=report.company, ticker=report.ticker,
            breach_date=report.breach_date,
            steps=[CalculationStepModel(**s.__dict__) for s in report.steps],
            final_score=report.final_score, final_prediction=report.final_prediction,
            confidence=report.confidence, probabilities=report.probabilities,
            feature_contributions=report.feature_contributions,
            methodology=report.methodology, limitations=report.limitations,
        )

    @router.post("/api/explain/auto", response_model=ExplainResponse)
    @limiter.limit("5/minute")
    async def explain_auto(request: Request, req: ExplainRequest):
        from ..breach_search import search_breach_incidents

        ticker = resolve_ticker(req.company)
        if ticker is None:
            raise TickerResolutionError(req.company)

        ticker = validate_ticker(ticker)
        company_name = resolve_company_name_from_ticker(ticker)

        incidents = await asyncio.to_thread(search_breach_incidents, company_name, 5)
        if incidents:
            top = max(incidents, key=lambda x: (x.records_affected, x.confidence))
            breach_date = top.date if top.date else req.breach_date
            records = top.records_affected if top.records_affected > 0 else req.records_affected
            breach_type = top.breach_type
        else:
            breach_date = req.breach_date
            records = req.records_affected
            breach_type = req.breach_type

        benchmark = detect_benchmark(ticker)

        stock_data, market_data = await asyncio.gather(
            asyncio.to_thread(fetch_stock_data, ticker, "2015-01-01"),
            asyncio.to_thread(fetch_market_data, "2015-01-01", benchmark),
        )
        if stock_data.empty:
            raise NoStockDataError(ticker)

        event = BreachEvent(
            company_name=company_name, ticker=ticker,
            breach_date=pd.Timestamp(breach_date),
            pwn_count=records, breach_type=breach_type,
            stock_data=stock_data, market_data=market_data,
            benchmark=benchmark,
        )

        features = await asyncio.to_thread(compute_features, event)
        if features is None:
            raise InsufficientDataError(company_name, breach_date)

        model = get_or_train_model()
        report = generate_explanation(event, features, model)

        return ExplainResponse(
            company=report.company, ticker=report.ticker,
            breach_date=report.breach_date,
            steps=[CalculationStepModel(**s.__dict__) for s in report.steps],
            final_score=report.final_score, final_prediction=report.final_prediction,
            confidence=report.confidence, probabilities=report.probabilities,
            feature_contributions=report.feature_contributions,
            methodology=report.methodology, limitations=report.limitations,
        )

    return router

"""Upload endpoints: /api/upload, /api/upload/analyze, /api/upload/config, /api/upload/analyze/config."""

from __future__ import annotations

import asyncio

import pandas as pd
from fastapi import APIRouter, HTTPException, Request, UploadFile, File

from ..schemas import (
    UploadConfigRequest, UploadResponse, BatchResult, BatchResponse,
)
from ..feature_engine import BreachEvent, compute_features_batch
from ..ticker_resolver import detect_benchmark
from ..stock_loader import fetch_stock_data, fetch_market_data, fetch_stock_batch
from ..preprocessor import preprocess_dataset, PreprocessConfig
from ..services.file_upload import validate_upload_extension, save_upload, cleanup_upload
from ..services.model import get_or_train_model, predict_severity
import structlog

log = structlog.get_logger(__name__)


def create_upload_routes(limiter) -> APIRouter:
    router = APIRouter()

    def _run_analysis_pipeline(preprocess_result) -> list[dict]:
        df = preprocess_result.df

        tickers = [str(t) for t in df["ticker"].dropna().unique() if t]
        stock_cache = fetch_stock_batch(tickers, start="2010-01-01")

        model = get_or_train_model()

        events = []
        skipped = []
        for _, row in df.iterrows():
            company = str(row.get("company_name", ""))
            ticker = str(row.get("ticker", ""))
            breach_date = row.get("breach_date")
            records = int(row.get("records_affected", 0))
            breach_type = str(row.get("breach_type", "data_leak"))

            if not company or pd.isna(breach_date) or not ticker or ticker == "nan":
                skipped.append({
                    "company": company, "ticker": ticker or "N/A",
                    "breach_date": str(breach_date)[:10] if not pd.isna(breach_date) else "N/A",
                    "records_affected": records, "breach_type": breach_type,
                    "risk_score": 0, "prediction": "unknown", "confidence": 0,
                    "probabilities": {}, "status": "skipped",
                    "error": "Missing company, date, or ticker",
                })
                continue

            stock_data = stock_cache.get(ticker, pd.DataFrame())
            if stock_data.empty:
                skipped.append({
                    "company": company, "ticker": ticker,
                    "breach_date": str(breach_date)[:10],
                    "records_affected": records, "breach_type": breach_type,
                    "risk_score": 0, "prediction": "unknown", "confidence": 0,
                    "probabilities": {}, "status": "failed",
                    "error": f"No stock data for {ticker}",
                })
                continue

            bm = detect_benchmark(ticker)
            market_data = fetch_market_data(start="2010-01-01", benchmark=bm)
            events.append(BreachEvent(
                company_name=company, ticker=ticker,
                breach_date=pd.Timestamp(breach_date),
                pwn_count=records, breach_type=breach_type,
                stock_data=stock_data, market_data=market_data,
                benchmark=bm,
            ))

        features_df = compute_features_batch(events)

        results = []
        for _, feat_row in features_df.iterrows():
            features_dict = feat_row.to_dict()
            features_df_single = pd.DataFrame([features_dict])
            try:
                pred = predict_severity(model, features_df_single)
                results.append({
                    "company": features_dict["company_name"],
                    "ticker": features_dict["ticker"],
                    "breach_date": features_dict["breach_date"],
                    "records_affected": int(features_dict["pwn_count"]),
                    "breach_type": features_dict["breach_type"],
                    "risk_score": pred["risk_score"], "prediction": pred["prediction"],
                    "confidence": pred["confidence"], "probabilities": pred["probabilities"],
                    "status": "ok",
                })
            except Exception as e:
                results.append({
                    "company": features_dict.get("company_name", "?"),
                    "ticker": features_dict.get("ticker", "?"),
                    "breach_date": features_dict.get("breach_date", "?"),
                    "records_affected": int(features_dict.get("pwn_count", 0)),
                    "breach_type": features_dict.get("breach_type", "?"),
                    "risk_score": 0, "prediction": "error", "confidence": 0,
                    "probabilities": {}, "status": "failed", "error": str(e),
                })

        return results + skipped

    @router.post("/api/upload", response_model=UploadResponse)
    @limiter.limit("5/minute")
    async def upload_dataset(request: Request, file: UploadFile = File(...)):
        suffix = validate_upload_extension(file.filename)
        tmp_path = None
        try:
            tmp_path = await save_upload(file, suffix)
            result = await asyncio.to_thread(preprocess_dataset, str(tmp_path))
            return UploadResponse(
                success=result.success,
                original_rows=result.original_rows,
                cleaned_rows=result.cleaned_rows,
                columns_detected=result.columns_detected,
                column_mapping=result.column_mapping,
                ticker_resolution_rate=result.ticker_resolution_rate,
                preview=result.preview,
                errors=result.errors,
                warnings=result.warnings,
            )
        except HTTPException:
            raise
        except Exception as e:
            log.error("upload_failed", error=str(e))
            raise HTTPException(status_code=500, detail="Upload failed")
        finally:
            cleanup_upload(tmp_path)

    @router.post("/api/upload/analyze", response_model=BatchResponse)
    @limiter.limit("2/minute")
    async def upload_and_analyze(request: Request, file: UploadFile = File(...)):
        suffix = validate_upload_extension(file.filename)
        tmp_path = None
        try:
            tmp_path = await save_upload(file, suffix)
            result = await asyncio.to_thread(preprocess_dataset, str(tmp_path))
        finally:
            cleanup_upload(tmp_path)

        if not result.success or result.df is None:
            return BatchResponse(total=0, analyzed=0, failed=0, results=[])

        raw_results = await asyncio.to_thread(_run_analysis_pipeline, result)
        results = [BatchResult(**r) for r in raw_results]
        analyzed = sum(1 for r in results if r.status == "ok")

        return BatchResponse(total=len(results), analyzed=analyzed, failed=len(results)-analyzed, results=results)

    @router.post("/api/upload/config", response_model=UploadResponse)
    @limiter.limit("5/minute")
    async def upload_with_config(request: Request, file: UploadFile = File(...), config: UploadConfigRequest = None):
        if config is None:
            config = UploadConfigRequest()

        suffix = validate_upload_extension(file.filename)
        tmp_path = None
        try:
            tmp_path = await save_upload(file, suffix)

            preprocess_config = PreprocessConfig(
                column_mapping=config.column_mapping,
                date_format=config.date_format,
                records_threshold=config.records_threshold,
                start_date=config.start_date,
                end_date=config.end_date,
                ticker_overrides=config.ticker_overrides,
                skip_ticker_resolution=config.skip_ticker_resolution,
                max_rows=config.max_rows,
            )
            result = await asyncio.to_thread(preprocess_dataset, str(tmp_path), preprocess_config)
            return UploadResponse(
                success=result.success, original_rows=result.original_rows,
                cleaned_rows=result.cleaned_rows, columns_detected=result.columns_detected,
                column_mapping=result.column_mapping, ticker_resolution_rate=result.ticker_resolution_rate,
                preview=result.preview, errors=result.errors, warnings=result.warnings,
            )
        except HTTPException:
            raise
        except Exception as e:
            log.error("upload_preprocessing_failed", error=str(e))
            raise HTTPException(status_code=500, detail="Preprocessing failed")
        finally:
            cleanup_upload(tmp_path)

    @router.post("/api/upload/analyze/config", response_model=BatchResponse)
    @limiter.limit("2/minute")
    async def upload_analyze_with_config(request: Request, file: UploadFile = File(...), config: UploadConfigRequest = None):
        if config is None:
            config = UploadConfigRequest()

        suffix = validate_upload_extension(file.filename)
        tmp_path = None
        try:
            tmp_path = await save_upload(file, suffix)

            preprocess_config = PreprocessConfig(
                column_mapping=config.column_mapping,
                date_format=config.date_format,
                records_threshold=config.records_threshold,
                start_date=config.start_date,
                end_date=config.end_date,
                ticker_overrides=config.ticker_overrides,
                skip_ticker_resolution=config.skip_ticker_resolution,
                max_rows=config.max_rows,
            )
            result = await asyncio.to_thread(preprocess_dataset, str(tmp_path), preprocess_config)
        except HTTPException:
            raise
        except Exception as e:
            log.error("upload_preprocessing_failed", error=str(e))
            raise HTTPException(status_code=500, detail="Preprocessing failed")
        finally:
            cleanup_upload(tmp_path)

        if not result.success or result.df is None:
            return BatchResponse(total=0, analyzed=0, failed=0, results=[])

        df = result.df

        tickers = [str(t) for t in df["ticker"].dropna().unique() if t]
        stock_cache = fetch_stock_batch(tickers, start=config.start_date if hasattr(config, 'start_date') else "2010-01-01")

        model = get_or_train_model()

        events = []
        skipped = []
        for _, row in df.iterrows():
            company = str(row.get("company_name", ""))
            ticker = str(row.get("ticker", ""))
            breach_date = row.get("breach_date")
            records = int(row.get("records_affected", 0))
            breach_type = str(row.get("breach_type", "data_leak"))

            if not company or pd.isna(breach_date) or not ticker or ticker == "nan":
                skipped.append(BatchResult(
                    company=company, ticker=ticker or "N/A",
                    breach_date=str(breach_date)[:10] if not pd.isna(breach_date) else "N/A",
                    records_affected=records, breach_type=breach_type,
                    risk_score=0, prediction="unknown", confidence=0,
                    probabilities={}, status="skipped",
                    error="Missing company, date, or ticker",
                ))
                continue

            stock_data = stock_cache.get(ticker, pd.DataFrame())
            if stock_data.empty:
                skipped.append(BatchResult(
                    company=company, ticker=ticker, breach_date=str(breach_date)[:10],
                    records_affected=records, breach_type=breach_type,
                    risk_score=0, prediction="unknown", confidence=0,
                    probabilities={}, status="failed", error=f"No stock data for {ticker}",
                ))
                continue

            bm = detect_benchmark(ticker)
            market_data = fetch_market_data(start="2010-01-01", benchmark=bm)
            events.append(BreachEvent(
                company_name=company, ticker=ticker,
                breach_date=pd.Timestamp(breach_date),
                pwn_count=records, breach_type=breach_type,
                stock_data=stock_data, market_data=market_data,
                benchmark=bm,
            ))

        features_df = compute_features_batch(events)

        results = []
        for _, feat_row in features_df.iterrows():
            features_dict = feat_row.to_dict()
            features_df_single = pd.DataFrame([features_dict])
            try:
                pred = predict_severity(model, features_df_single)
                results.append(BatchResult(
                    company=features_dict["company_name"], ticker=features_dict["ticker"],
                    breach_date=features_dict["breach_date"],
                    records_affected=int(features_dict["pwn_count"]),
                    breach_type=features_dict["breach_type"],
                    risk_score=pred["risk_score"], prediction=pred["prediction"],
                    confidence=pred["confidence"], probabilities=pred["probabilities"],
                    status="ok",
                ))
            except Exception as e:
                results.append(BatchResult(
                    company=features_dict.get("company_name", "?"),
                    ticker=features_dict.get("ticker", "?"),
                    breach_date=features_dict.get("breach_date", "?"),
                    records_affected=int(features_dict.get("pwn_count", 0)),
                    breach_type=features_dict.get("breach_type", "?"),
                    risk_score=0, prediction="error", confidence=0,
                    probabilities={}, status="failed", error=str(e),
                ))

        all_results = results + skipped
        analyzed = sum(1 for r in all_results if r.status == "ok")
        failed = sum(1 for r in all_results if r.status in ("failed", "skipped"))

        return BatchResponse(total=len(all_results), analyzed=analyzed, failed=failed, results=all_results)

    return router

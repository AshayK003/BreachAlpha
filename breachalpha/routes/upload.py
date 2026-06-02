"""Upload endpoints: /api/upload, /api/upload/analyze, /api/upload/config, /api/upload/analyze/config."""

from __future__ import annotations

import asyncio

import structlog
from fastapi import APIRouter, HTTPException, Request, UploadFile, File

from ..schemas import (
    UploadConfigRequest, UploadResponse, BatchResult, BatchResponse,
)
from ..preprocessor import preprocess_dataset, PreprocessConfig
from ..services.file_upload import validate_upload_extension, save_upload, cleanup_upload
from ..services.model import run_analysis_pipeline

log = structlog.get_logger(__name__)


def _preprocess_dataset(tmp_path_str: str, config: UploadConfigRequest = None):
    """Run preprocessing synchronously. Called via asyncio.to_thread."""
    preprocess_config = None
    if config is not None:
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
    return preprocess_dataset(tmp_path_str, preprocess_config)


def _to_upload_response(result) -> UploadResponse:
    """Convert a preprocess result to an UploadResponse."""
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


def create_upload_routes(limiter) -> APIRouter:
    router = APIRouter()

    @router.post("/api/upload", response_model=UploadResponse)
    @limiter.limit("5/minute")
    async def upload_dataset(request: Request, file: UploadFile = File(...)):
        suffix = validate_upload_extension(file.filename)
        tmp_path = None
        try:
            tmp_path = await save_upload(file, suffix)
            result = await asyncio.to_thread(_preprocess_dataset, str(tmp_path))
            return _to_upload_response(result)
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
            result = await asyncio.to_thread(_preprocess_dataset, str(tmp_path))
        except HTTPException:
            raise
        except Exception as e:
            log.error("upload_preprocessing_failed", error=str(e))
            raise HTTPException(status_code=500, detail="Preprocessing failed")
        finally:
            cleanup_upload(tmp_path)

        if not result.success or result.df is None:
            return BatchResponse(total=0, analyzed=0, failed=0, results=[])

        raw_results = await asyncio.to_thread(run_analysis_pipeline, result)
        results = [BatchResult(**r) for r in raw_results]
        analyzed = sum(1 for r in results if r.status == "ok")

        return BatchResponse(
            total=len(results), analyzed=analyzed,
            failed=len(results) - analyzed, results=results,
        )

    @router.post("/api/upload/config", response_model=UploadResponse)
    @limiter.limit("5/minute")
    async def upload_with_config(request: Request, file: UploadFile = File(...), config: UploadConfigRequest = None):
        if config is None:
            config = UploadConfigRequest()

        suffix = validate_upload_extension(file.filename)
        tmp_path = None
        try:
            tmp_path = await save_upload(file, suffix)
            result = await asyncio.to_thread(_preprocess_dataset, str(tmp_path), config)
            return _to_upload_response(result)
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
            result = await asyncio.to_thread(_preprocess_dataset, str(tmp_path), config)
        except HTTPException:
            raise
        except Exception as e:
            log.error("upload_preprocessing_failed", error=str(e))
            raise HTTPException(status_code=500, detail="Preprocessing failed")
        finally:
            cleanup_upload(tmp_path)

        if not result.success or result.df is None:
            return BatchResponse(total=0, analyzed=0, failed=0, results=[])

        start_date = config.start_date if hasattr(config, 'start_date') else "2010-01-01"
        raw_results = await asyncio.to_thread(run_analysis_pipeline, result, start_date)
        results = [BatchResult(**r) for r in raw_results]
        analyzed = sum(1 for r in results if r.status == "ok")
        failed = sum(1 for r in results if r.status in ("failed", "skipped"))

        return BatchResponse(
            total=len(results), analyzed=analyzed,
            failed=failed, results=results,
        )

    return router

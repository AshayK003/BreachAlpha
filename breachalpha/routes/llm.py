"""LLM integration endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ..schemas import LLMAnalysisRequest, LLMRiskRequest, LLMQuestionRequest


def create_llm_routes(limiter) -> APIRouter:
    router = APIRouter()

    @router.get("/api/llm/status")
    @limiter.exempt
    async def llm_status(request: Request):
        import asyncio
        from ..llm_integration import check_lm_studio, LLMConfig
        config = LLMConfig()
        status = await asyncio.to_thread(check_lm_studio, config)
        return {
            "available": status["available"],
            "url": status["url"],
            "models": status.get("models", []),
            "default_model": status.get("default_model", ""),
            "error": status.get("error"),
        }

    @router.post("/api/llm/analyze-dataset")
    @limiter.limit("5/minute")
    async def llm_analyze_dataset(request: Request, req: LLMAnalysisRequest):
        import asyncio
        from ..llm_integration import analyze_breach_dataset, LLMConfig

        config = LLMConfig()
        if req.model:
            config.model = req.model

        result = await asyncio.to_thread(analyze_breach_dataset,
            dataset_summary=req.dataset_summary,
            analysis_results=req.analysis_results,
            config=config,
        )

        if result is None:
            raise HTTPException(status_code=503, detail="LLM unavailable. Check BREACHALPHA_LLM_URL env var.")

        return {"analysis": result, "model": config.model}

    @router.post("/api/llm/risk-summary")
    @limiter.limit("10/minute")
    async def llm_risk_summary(request: Request, req: LLMRiskRequest):
        import asyncio
        from ..llm_integration import generate_risk_summary, LLMConfig

        config = LLMConfig()
        result = await asyncio.to_thread(generate_risk_summary,
            company=req.company, risk_score=req.risk_score,
            prediction=req.prediction, features=req.features, config=config,
        )

        if result is None:
            raise HTTPException(status_code=503, detail="LLM unavailable. Check BREACHALPHA_LLM_URL env var.")

        return {"summary": result, "model": config.model}

    @router.post("/api/llm/ask")
    @limiter.limit("10/minute")
    async def llm_ask(request: Request, req: LLMQuestionRequest):
        import asyncio
        from ..llm_integration import answer_breach_question, LLMConfig

        config = LLMConfig()
        result = await asyncio.to_thread(answer_breach_question,
            question=req.question, context=req.context, config=config,
        )

        if result is None:
            raise HTTPException(status_code=503, detail="LLM unavailable. Check BREACHALPHA_LLM_URL env var.")

        return {"answer": result, "model": config.model}

    @router.post("/api/llm/enrich")
    @limiter.limit("5/minute")
    async def llm_enrich_records(request: Request, records: list[dict]):
        import asyncio
        from ..llm_integration import enrich_breach_records, LLMConfig

        config = LLMConfig()
        enriched = await asyncio.to_thread(enrich_breach_records, records, config=config)

        if enriched is None:
            raise HTTPException(status_code=503, detail="LLM unavailable. Check BREACHALPHA_LLM_URL env var.")

        return {"enriched": enriched, "count": len(enriched), "model": config.model}

    return router

"""Pydantic request/response schemas for the BreachAlpha API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ── Request Models ──────────────────────────────────────────────────────


class ScoreRequest(BaseModel):
    company: str = Field(..., description="Company name (e.g., 'Equifax')")
    breach_type: str = Field(default="data_leak", description="Breach type: data_leak, ransomware, hack, etc.")
    records_affected: int = Field(default=1_000_000, description="Number of records affected")
    breach_date: str = Field(default="2024-01-01", description="Breach date (YYYY-MM-DD)")


# ExplainRequest is identical to ScoreRequest -- use ScoreRequest everywhere


class TrainRequest(BaseModel):
    data_path: str = Field(..., description="Path to breach CSV file (must be in data/ directory)")


class AnalysisConfigRequest(BaseModel):
    """User-configurable analysis parameters."""
    estimation_window: int = Field(default=250, ge=50, le=500, description="Days for market model estimation")
    pre_event_window: int = Field(default=30, ge=5, le=100, description="Days before event to analyze")
    post_event_window: int = Field(default=60, ge=10, le=200, description="Days after event to analyze")
    recovery_max_days: int = Field(default=90, ge=10, le=365, description="Max days to search for recovery")
    threshold_critical: float = Field(default=-0.15, ge=-1.0, le=0.0, description="CAR threshold for critical severity")
    threshold_high: float = Field(default=-0.07, ge=-1.0, le=0.0, description="CAR threshold for high severity")
    threshold_medium: float = Field(default=-0.02, ge=-1.0, le=0.0, description="CAR threshold for medium severity")
    car_short_start: int = Field(default=-1, description="CAR short window start (days relative to event)")
    car_short_end: int = Field(default=1, description="CAR short window end")
    car_long_start: int = Field(default=-5, description="CAR long window start")
    car_long_end: int = Field(default=30, description="CAR long window end")
    benchmark: str = Field(default="^GSPC", description="Market benchmark ticker (^GSPC for S&P 500)")
    start_date: str = Field(default="2010-01-01", description="Start date for stock data")
    min_records: int = Field(default=1000, ge=0, description="Minimum records affected filter")


class UploadConfigRequest(BaseModel):
    """User-configurable preprocessing options."""
    column_mapping: dict[str, str] = Field(default_factory=dict, description="Custom column name mapping")
    date_format: Optional[str] = Field(default=None, description="Preferred date format (e.g., %Y-%m-%d)")
    records_threshold: int = Field(default=1000, ge=0, description="Minimum records affected filter")
    start_date: Optional[str] = Field(default=None, description="Filter breaches after this date")
    end_date: Optional[str] = Field(default=None, description="Filter breaches before this date")
    ticker_overrides: dict[str, str] = Field(default_factory=dict, description="Custom company→ticker mappings")
    skip_ticker_resolution: bool = Field(default=False, description="Skip automatic ticker resolution")
    max_rows: Optional[int] = Field(default=None, ge=1, description="Max rows to read from file")


class DataSourceConfigRequest(BaseModel):
    """Configure data source preferences."""
    primary_source: str = Field(default="yfinance", description="Primary data source")
    alpha_vantage_key: str = Field(default="", description="Alpha Vantage API key")
    enable_fallback: bool = Field(default=True, description="Enable fallback sources")
    cache_ttl_hours: int = Field(default=24, ge=1, le=168, description="Cache TTL in hours")


class LLMAnalysisRequest(BaseModel):
    dataset_summary: str = Field(..., description="Summary of the dataset")
    analysis_results: str = Field(..., description="Results from numerical analysis")
    model: str = Field(default="", description="Model name (empty = default)")


class LLMRiskRequest(BaseModel):
    company: str
    risk_score: float
    prediction: str
    features: dict


class LLMQuestionRequest(BaseModel):
    question: str = Field(..., description="Question about breach data")
    context: str = Field(default="", description="Additional context")


# ── Response Models ─────────────────────────────────────────────────────


class FeatureDetail(BaseModel):
    abnormal_return_day0: float
    abnormal_return_day1: float
    abnormal_return_day5: float
    abnormal_return_day30: float
    car_minus1_plus1: float
    car_minus5_plus30: float
    volatility_spike: float
    volume_change: float
    time_to_recovery: Optional[int]
    severity: str

    @classmethod
    def from_features(cls, features, severity: str) -> FeatureDetail:
        """Build a FeatureDetail from a BreachFeatures dataclass."""
        return cls(
            abnormal_return_day0=features.abnormal_return_day0,
            abnormal_return_day1=features.abnormal_return_day1,
            abnormal_return_day5=features.abnormal_return_day5,
            abnormal_return_day30=features.abnormal_return_day30,
            car_minus1_plus1=features.car_minus1_plus1,
            car_minus5_plus30=features.car_minus5_plus30,
            volatility_spike=features.volatility_spike,
            volume_change=features.volume_change,
            time_to_recovery=features.time_to_recovery,
            severity=severity,
        )


class ScoreResponse(BaseModel):
    company: str
    ticker: str
    risk_score: float
    prediction: str
    confidence: float
    probabilities: dict[str, float]
    features: FeatureDetail


class AutoScoreResponse(ScoreResponse):
    breach_found: bool
    breach_date_used: str
    records_used: int
    breach_type_used: str
    breach_confidence: float
    incident_count: int


class DemoCase(BaseModel):
    company: str
    ticker: str
    breach_date: str
    pwn_count: int
    breach_type: str
    description: str
    risk_score: Optional[float] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None


class TrainResponse(BaseModel):
    status: str
    n_samples: int
    cv_accuracy: float
    cv_std: float
    feature_importance: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str


class UploadResponse(BaseModel):
    success: bool
    original_rows: int
    cleaned_rows: int
    columns_detected: list[str]
    column_mapping: dict[str, str]
    ticker_resolution_rate: float
    preview: list[dict]
    errors: list[str]
    warnings: list[str]


class BatchResult(BaseModel):
    company: str
    ticker: str
    breach_date: str
    records_affected: int
    breach_type: str
    risk_score: float
    prediction: str
    confidence: float
    probabilities: dict[str, float]
    status: str
    error: Optional[str] = None


class BatchResponse(BaseModel):
    total: int
    analyzed: int
    failed: int
    results: list[BatchResult]


class CalculationStepModel(BaseModel):
    step_number: int
    name: str
    description: str
    formula: str
    inputs: dict
    output: float | str | dict
    interpretation: str


class ExplainResponse(BaseModel):
    company: str
    ticker: str
    breach_date: str
    steps: list[CalculationStepModel]
    final_score: float
    final_prediction: str
    confidence: float
    probabilities: dict[str, float]
    feature_contributions: dict[str, float]
    methodology: str
    limitations: list[str]


class CacheInfoResponse(BaseModel):
    cached_files: int
    total_size_kb: float
    tickers: list[str]


class ConfigPreset(BaseModel):
    name: str
    description: str
    config: AnalysisConfigRequest


class DataSourceStatus(BaseModel):
    name: str
    available: bool
    priority: int
    reason: Optional[str] = None


class DataSourceConfigResponse(BaseModel):
    primary_source: str
    alpha_vantage_key_set: bool
    enable_fallback: bool
    cache_ttl_hours: int
    sources: dict[str, DataSourceStatus]


# ── LLM Response Models ──────────────────────────────────────────────────


class LLMStatusResponse(BaseModel):
    available: bool
    url: str
    models: list[str]
    default_model: str
    error: Optional[str] = None


class LLMAnalysisResponse(BaseModel):
    analysis: str
    model: str


class LLMSummaryResponse(BaseModel):
    summary: str
    model: str


class LLMAnswerResponse(BaseModel):
    answer: str
    model: str


class LLMEnrichResponse(BaseModel):
    enriched: list[dict]
    count: int
    model: str


# ── Search Response Models ────────────────────────────────────────────────


class SearchResult(BaseModel):
    symbol: str
    name: str
    ticker_full: str
    source: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    count: int


class BreachIncidentResult(BaseModel):
    company: str
    date: Optional[str] = None
    breach_type: str
    records_affected: int
    source: str
    description: str
    confidence: float


class BreachSearchResponse(BaseModel):
    query: str
    incidents: list[BreachIncidentResult]
    count: int

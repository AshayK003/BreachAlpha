"""Shared constants used across BreachAlpha modules.

Single source of truth for risk weights, feature columns, severity labels,
upload limits, and other cross-cutting constants.
"""

from __future__ import annotations

import re

# ── Risk Score Weights ──────────────────────────────────────────────────
# Used in: model.py predict_severity, server.py batch prediction,
#          explainability.py risk score calculation
RISK_WEIGHTS: dict[str, int] = {
    "low": 10,
    "medium": 35,
    "high": 65,
    "critical": 95,
}

# ── Feature Columns ─────────────────────────────────────────────────────
# Used in: model.py (training + prediction), server.py (batch prediction)
FEATURE_COLS: list[str] = [
    "abnormal_return_day0",
    "abnormal_return_day1",
    "abnormal_return_day5",
    "abnormal_return_day30",
    "car_minus1_plus1",
    "car_minus5_plus30",
    "volatility_spike",
    "volume_change",
    "time_to_recovery",
    "pwn_count",
]

# ── Severity Labels ─────────────────────────────────────────────────────
# Used in: model.py, feature_engine.py, server.py, explainability.py
SEVERITY_LABELS: list[str] = ["low", "medium", "high", "critical"]
SEVERITY_MAP: dict[str, int] = {label: idx for idx, label in enumerate(SEVERITY_LABELS)}

# ── Upload Limits ───────────────────────────────────────────────────────
MAX_UPLOAD_BYTES: int = 50 * 1024 * 1024  # 50 MB
ALLOWED_UPLOAD_EXTENSIONS: set[str] = {".csv", ".xlsx", ".xls", ".tsv"}

# ── Validation ──────────────────────────────────────────────────────────
TICKER_RE: re.Pattern = re.compile(r"^[A-Z0-9.^]{1,15}$")

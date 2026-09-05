"""Regression tests for the Sep 2026 audit fixes (P0/P1/P2).

Each test pins one verified bug so it can never silently return.
"""

import numpy as np
import pandas as pd
import pytest

from breachalpha.core.constants import TRAIN_FEATURE_COLS
from breachalpha.model import prepare_training_data, train_model
from breachalpha.schemas import ScoreRequest
from breachalpha.ticker_resolver import resolve_ticker


def _features(n=60, seed=7):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "abnormal_return_day0": rng.normal(-0.02, 0.05, n),
        "abnormal_return_day1": rng.normal(-0.01, 0.04, n),
        "abnormal_return_day5": rng.normal(-0.005, 0.03, n),
        "abnormal_return_day30": rng.normal(0.001, 0.02, n),
        "car_minus1_plus1": rng.normal(-0.03, 0.08, n),
        "car_minus5_plus30": rng.normal(-0.05, 0.12, n),
        "volatility_spike": rng.uniform(0.8, 3.0, n),
        "volume_change": rng.uniform(0.5, 5.0, n),
        "time_to_recovery": rng.integers(1, 60, n).astype(float),
        "pwn_count": rng.integers(1000, 10_000_000, n),
    })


def test_no_label_leakage_in_training_matrix():
    X, y = prepare_training_data(_features())
    assert "car_minus5_plus30" not in X.columns
    assert list(X.columns) == TRAIN_FEATURE_COLS


def test_trained_model_feature_count_matches_serve():
    res = train_model(_features(80))
    assert res["feature_cols"] == TRAIN_FEATURE_COLS
    assert set(res["metrics"]["feature_importance"]) == set(TRAIN_FEATURE_COLS)


def test_unknown_names_resolve_to_none():
    for bad in ["UNKNOWN", "QZXJ", "XQZ", "FakeCompany123", "Xyzzy Plugh"]:
        assert resolve_ticker(bad) is None, bad
    # ...while genuine single-letter tickers still resolve.
    assert resolve_ticker("C") == "C"


def test_known_tickers_still_resolve():
    assert resolve_ticker("Equifax") == "EFX"
    assert resolve_ticker("MSFT") == "MSFT"
    assert resolve_ticker("Capital One Financial Corp") == "COF"
    assert resolve_ticker("TATAPOWER.NS") == "TATAPOWER.NS"
    assert resolve_ticker("tech mahindra") == "TECHM.NS"
    assert resolve_ticker("tata communications") == "TATACOMM.NS"


def test_score_request_rejects_garbage():
    with pytest.raises(Exception):
        ScoreRequest(company="x" * 201, breach_date="2024-01-01")
    with pytest.raises(Exception):
        ScoreRequest(company="Equifax", records_affected=-5)
    with pytest.raises(Exception):
        ScoreRequest(company="Equifax", breach_date="not-a-date")
    ok = ScoreRequest(company="Equifax", breach_date="2024-01-01")
    assert ok.records_affected == 1_000_000


def test_llm_config_rejects_non_http():
    from breachalpha.llm_integration import LLMConfig
    with pytest.raises(ValueError):
        LLMConfig(base_url="file:///etc/passwd")
    assert LLMConfig(base_url="http://127.0.0.1:1234/v1").base_url.startswith("http")


def test_oversize_upload_leaves_no_partial(tmp_path):
    import asyncio
    from unittest.mock import Mock
    from breachalpha.services.file_upload import save_upload, MAX_UPLOAD_BYTES
    from breachalpha.core.exceptions import FileTooLargeError

    big = b"x" * (MAX_UPLOAD_BYTES + 100)
    file = Mock()
    async def _read(n):
        if not hasattr(_read, "sent"):
            _read.sent = True
            return big
        return b""
    file.read = _read
    before = set(tmp_path.iterdir())
    import tempfile
    old_tmp = tempfile.tempdir
    tempfile.tempdir = str(tmp_path)
    try:
        with pytest.raises(FileTooLargeError):
            asyncio.run(save_upload(file, ".csv"))
    finally:
        tempfile.tempdir = old_tmp
    assert set(tmp_path.iterdir()) == before


def test_missingness_counted_before_fillna(tmp_path):
    from breachalpha.preprocessor import preprocess_dataset, PreprocessConfig
    csv = tmp_path / "m.csv"
    pd.DataFrame({
        "company_name": ["Equifax", "Unknown Corp", "Target"],
        "breach_date": ["2017-09-07", "2020-01-01", "2021-01-01"],
        "records_affected": [147_000_000, None, 5_000_000],
        "breach_type": ["data_leak", "hack", "ransomware"],
    }).to_csv(csv, index=False)
    out = preprocess_dataset(csv, PreprocessConfig(records_threshold=0))
    assert out.validation["missing_records"] == 1

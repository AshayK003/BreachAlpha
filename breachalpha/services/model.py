"""Model service.

Centralizes model loading, synthetic training fallback, and risk score
calculation. Eliminates 8x duplicated model-loading blocks in server.py.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from ..core.constants import RISK_WEIGHTS, SEVERITY_LABELS
from ..model import load_model, train_model, predict_severity

logger = logging.getLogger(__name__)

# Thread pool for parallel CPU-bound work (feature computation)
_compute_pool = ThreadPoolExecutor(max_workers=4)


def get_or_train_model():
    """Load the trained model, or train on synthetic data as fallback.

    Returns:
        A trained XGBClassifier (either loaded from disk or synthetic).
    """
    model = load_model()
    if model is None:
        logger.info("No trained model found — training on synthetic data")
        model = _train_synthetic()["model"]
    return model


def _train_synthetic() -> dict:
    """Train on synthetic data for demo/fallback purposes."""
    np.random.seed(42)
    n = 100
    synthetic = pd.DataFrame({
        "abnormal_return_day0": np.random.normal(-0.02, 0.05, n),
        "abnormal_return_day1": np.random.normal(-0.01, 0.04, n),
        "abnormal_return_day5": np.random.normal(-0.005, 0.03, n),
        "abnormal_return_day30": np.random.normal(0.001, 0.02, n),
        "car_minus1_plus1": np.random.normal(-0.03, 0.08, n),
        "car_minus5_plus30": np.random.normal(-0.05, 0.12, n),
        "volatility_spike": np.random.uniform(0.8, 3.0, n),
        "volume_change": np.random.uniform(0.5, 5.0, n),
        "time_to_recovery": np.random.choice([5, 10, 20, 30, 60, None], n),
        "pwn_count": np.random.lognormal(15, 2, n).astype(int),
    })
    return train_model(synthetic)


def score_features(model, features_df: pd.DataFrame) -> dict:
    """Score a single set of features using the model.

    Args:
        model: Trained XGBClassifier.
        features_df: Single-row DataFrame of features.

    Returns:
        Dict with prediction, probabilities, risk_score, confidence.
    """
    return predict_severity(model, features_df)


def batch_score(model, features_df: pd.DataFrame) -> list[dict]:
    """Batch-score multiple feature rows with fallback to per-row prediction.

    Args:
        model: Trained XGBClassifier.
        features_df: DataFrame of features (multiple rows).

    Returns:
        List of prediction dicts, one per row.
    """
    results = []
    try:
        from ..core.constants import FEATURE_COLS
        feature_cols = [c for c in FEATURE_COLS if c in features_df.columns]
        all_features = features_df[feature_cols].replace([np.inf, -np.inf], np.nan)
        if "time_to_recovery" in all_features.columns:
            all_features["time_to_recovery"] = pd.to_numeric(all_features["time_to_recovery"], errors="coerce")
        all_features = all_features.fillna(0)

        raw_predictions = model.predict(all_features)
        probas = model.predict_proba(all_features)

        for idx, prediction_idx in enumerate(raw_predictions):
            proba = probas[idx]
            prediction = SEVERITY_LABELS[int(prediction_idx)]
            probabilities = {label: float(p) for label, p in zip(SEVERITY_LABELS, proba)}
            risk_score = round(sum(probabilities[label] * RISK_WEIGHTS[label] for label in SEVERITY_LABELS), 1)
            confidence = round(float(max(proba)), 3)
            results.append({
                "prediction": prediction,
                "probabilities": probabilities,
                "risk_score": risk_score,
                "confidence": confidence,
            })
    except Exception as e:
        logger.warning("Batch prediction failed, falling back to per-row: %s", e)
        for _, feat_row in features_df.iterrows():
            try:
                fd = feat_row.to_dict()
                pred = predict_severity(model, pd.DataFrame([fd]))
                results.append(pred)
            except Exception as e2:
                results.append({
                    "prediction": "error",
                    "probabilities": {},
                    "risk_score": 0,
                    "confidence": 0,
                    "_error": str(e2),
                })

    return results


def run_analysis_pipeline(preprocess_result, start_date: str = "2010-01-01") -> list[dict]:
    """Run the full analysis pipeline on a preprocessed dataset.

    Builds BreachEvents, computes features, and batch-scores using the model.
    Shared by /api/upload/analyze and /api/upload/analyze/config endpoints.

    Args:
        preprocess_result: Result from preprocess_dataset() containing the cleaned DataFrame.
        start_date: Start date for stock data fetching.

    Returns:
        List of result dicts (one per row) with keys matching BatchResult.
    """
    from ..feature_engine import BreachEvent, compute_features_batch
    from ..ticker_resolver import detect_benchmark
    from ..stock_loader import fetch_stock_data, fetch_market_data, fetch_stock_batch

    df = preprocess_result.df

    # Batch-fetch stock data for all tickers
    tickers = [str(t) for t in df["ticker"].dropna().unique() if t]
    stock_cache = fetch_stock_batch(tickers, start=start_date)

    model = get_or_train_model()

    # Build events, collect skipped rows
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
        market_data = fetch_market_data(start=start_date, benchmark=bm)
        events.append(BreachEvent(
            company_name=company, ticker=ticker,
            breach_date=pd.Timestamp(breach_date),
            pwn_count=records, breach_type=breach_type,
            stock_data=stock_data, market_data=market_data,
            benchmark=bm,
        ))

    # Compute features for all events
    features_df = compute_features_batch(events)

    # Batch-score all features
    predictions = batch_score(model, features_df)

    # Build result dicts
    results = []
    for idx, (_, feat_row) in enumerate(features_df.iterrows()):
        features_dict = feat_row.to_dict()
        pred = predictions[idx]
        error = pred.pop("_error", None)
        results.append({
            "company": features_dict["company_name"],
            "ticker": features_dict["ticker"],
            "breach_date": features_dict["breach_date"],
            "records_affected": int(features_dict["pwn_count"]),
            "breach_type": features_dict["breach_type"],
            "risk_score": pred["risk_score"],
            "prediction": pred["prediction"],
            "confidence": pred["confidence"],
            "probabilities": pred["probabilities"],
            "status": "failed" if pred["prediction"] == "error" else "ok",
            **({"error": error} if error else {}),
        })

    return results + skipped

"""Tests for services/model.py — model loading, scoring, and batch scoring."""

import numpy as np
import pandas as pd
import pytest

from breachalpha.services.model import get_or_train_model, score_features, batch_score
from breachalpha.core.constants import FEATURE_COLS, SEVERITY_LABELS, RISK_WEIGHTS


class TestGetOrTrainModel:
    def test_returns_model(self):
        model = get_or_train_model()
        assert model is not None
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_returns_consistent_predictions(self):
        """Same input should produce same output (model is deterministic after training)."""
        model = get_or_train_model()
        np.random.seed(42)
        features = pd.DataFrame({col: [np.random.randn() * 0.05] for col in FEATURE_COLS})
        pred1 = model.predict(features)
        pred2 = model.predict(features)
        np.testing.assert_array_equal(pred1, pred2)


class TestScoreFeatures:
    def test_returns_valid_keys(self, trained_model, sample_features_df):
        result = score_features(trained_model, sample_features_df)
        assert "prediction" in result
        assert "probabilities" in result
        assert "risk_score" in result
        assert "confidence" in result

    def test_prediction_is_severity_label(self, trained_model, sample_features_df):
        result = score_features(trained_model, sample_features_df)
        assert result["prediction"] in SEVERITY_LABELS

    def test_probabilities_sum_to_one(self, trained_model, sample_features_df):
        result = score_features(trained_model, sample_features_df)
        total = sum(result["probabilities"].values())
        assert abs(total - 1.0) < 1e-6

    def test_risk_score_in_range(self, trained_model, sample_features_df):
        result = score_features(trained_model, sample_features_df)
        assert 0 <= result["risk_score"] <= 100

    def test_confidence_in_range(self, trained_model, sample_features_df):
        result = score_features(trained_model, sample_features_df)
        assert 0 <= result["confidence"] <= 1


class TestBatchScore:
    def test_batch_returns_list(self, trained_model, sample_features_df):
        results = batch_score(trained_model, sample_features_df)
        assert isinstance(results, list)
        assert len(results) == 1

    def test_batch_multiple_rows(self, trained_model, sample_features_dict):
        rows = []
        for i in range(3):
            row = sample_features_dict.copy()
            row["abnormal_return_day0"] = -0.01 * (i + 1)
            rows.append(row)
        df = pd.DataFrame(rows)
        results = batch_score(trained_model, df)
        assert len(results) == 3
        for r in results:
            assert "prediction" in r
            assert "risk_score" in r

    def test_batch_with_nan_values(self, trained_model, sample_features_dict):
        row = sample_features_dict.copy()
        row["time_to_recovery"] = None
        df = pd.DataFrame([row])
        results = batch_score(trained_model, df)
        assert len(results) == 1
        assert results[0]["prediction"] in SEVERITY_LABELS

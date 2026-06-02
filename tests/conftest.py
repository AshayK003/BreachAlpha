"""Shared test fixtures for BreachAlpha."""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


# ── Synthetic Data Factories ──────────────────────────────────────────────

@pytest.fixture
def sample_stock_data():
    """200 days of synthetic stock data with a -10% drop on day 100."""
    dates = pd.bdate_range("2020-01-01", periods=200)
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 200)
    returns[100] = -0.10
    returns[101] = -0.05
    prices = 100 * np.cumprod(1 + returns)
    volume = np.random.randint(1_000_000, 10_000_000, 200)
    return pd.DataFrame({
        "Open": prices * 0.99, "High": prices * 1.01,
        "Low": prices * 0.98, "Close": prices,
        "Volume": volume, "Dividends": 0.0, "Stock Splits": 0.0,
    }, index=dates)


@pytest.fixture
def sample_market_data():
    """200 days of synthetic S&P 500 data (no drop)."""
    dates = pd.bdate_range("2020-01-01", periods=200)
    np.random.seed(99)
    returns = np.random.normal(0.0005, 0.01, 200)
    prices = 3000 * np.cumprod(1 + returns)
    volume = np.random.randint(2_000_000, 4_000_000, 200)
    return pd.DataFrame({
        "Open": prices * 0.99, "High": prices * 1.01,
        "Low": prices * 0.98, "Close": prices,
        "Volume": volume, "Dividends": 0.0, "Stock Splits": 0.0,
    }, index=dates)


@pytest.fixture
def sample_features_dict():
    """A single row of features as a dict."""
    return {
        "company_name": "TestCorp", "ticker": "TST",
        "breach_date": "2020-06-15", "pwn_count": 1000000,
        "breach_type": "data_leak",
        "abnormal_return_day0": -0.05,
        "abnormal_return_day1": -0.03,
        "abnormal_return_day5": -0.01,
        "abnormal_return_day30": 0.005,
        "car_minus1_plus1": -0.08,
        "car_minus5_plus30": -0.12,
        "volatility_spike": 2.0,
        "volume_change": 3.0,
        "time_to_recovery": 25,
    }


@pytest.fixture
def sample_features_df(sample_features_dict):
    """A single-row DataFrame of features."""
    return pd.DataFrame([sample_features_dict])


@pytest.fixture
def sample_breach_event(sample_stock_data, sample_market_data):
    """A valid BreachEvent for testing."""
    from breachalpha.feature_engine import BreachEvent
    return BreachEvent(
        company_name="TestCorp",
        ticker="TST",
        breach_date=pd.Timestamp("2020-06-15"),
        pwn_count=1_000_000,
        breach_type="data_leak",
        stock_data=sample_stock_data,
        market_data=sample_market_data,
    )


@pytest.fixture
def trained_model():
    """A trained XGBoost model (synthetic data)."""
    from breachalpha.services.model import get_or_train_model
    return get_or_train_model()


@pytest.fixture
def mock_stock_data(sample_stock_data):
    """Mock fetch_stock_data to return synthetic data without network."""
    with patch("breachalpha.routes.score.fetch_stock_data", return_value=sample_stock_data):
        with patch("breachalpha.routes.explain.fetch_stock_data", return_value=sample_stock_data):
            with patch("breachalpha.routes.meta.fetch_stock_data", return_value=sample_stock_data):
                yield sample_stock_data


@pytest.fixture
def mock_market_data(sample_market_data):
    """Mock fetch_market_data to return synthetic data without network."""
    with patch("breachalpha.routes.score.fetch_market_data", return_value=sample_market_data):
        with patch("breachalpha.routes.explain.fetch_market_data", return_value=sample_market_data):
            with patch("breachalpha.routes.meta.fetch_market_data", return_value=sample_market_data):
                yield sample_market_data


@pytest.fixture
def client():
    """FastAPI TestClient for API tests."""
    from fastapi.testclient import TestClient
    from breachalpha.server import app
    return TestClient(app)

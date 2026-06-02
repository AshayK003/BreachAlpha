"""API integration tests for routes — using TestClient with mocked externals."""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"

    def test_health_reports_model_status(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)


class TestConfigPresets:
    def test_presets_returns_list(self, client):
        response = client.get("/api/config/presets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_preset_has_required_fields(self, client):
        response = client.get("/api/config/presets")
        presets = response.json()
        for preset in presets:
            assert "name" in preset
            assert "description" in preset
            assert "config" in preset

    def test_preset_names_are_unique(self, client):
        response = client.get("/api/config/presets")
        names = [p["name"] for p in response.json()]
        assert len(names) == len(set(names))


class TestScoreEndpoint:
    def test_score_unknown_company_returns_404(self, client):
        response = client.post("/api/score", json={
            "company": "NonexistentCompany999",
            "breach_date": "2024-01-01",
            "records_affected": 1000,
            "breach_type": "data_leak",
        })
        assert response.status_code == 404

    def test_score_missing_body_returns_422(self, client):
        response = client.post("/api/score", json={})
        assert response.status_code == 422

    def test_score_missing_company_returns_422(self, client):
        response = client.post("/api/score", json={
            "breach_date": "2024-01-01",
            "records_affected": 1000,
            "breach_type": "data_leak",
        })
        assert response.status_code == 422


class TestSearchEndpoint:
    def test_empty_query_returns_empty(self, client):
        response = client.get("/api/search?q=")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0

    def test_known_company_returns_results(self, client):
        response = client.get("/api/search?q=microsoft&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0
        assert any("MSFT" in r.get("symbol", "") or "MSFT" in r.get("ticker_full", "") for r in data["results"])

    def test_partial_match_returns_results(self, client):
        response = client.get("/api/search?q=equi&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] > 0


class TestBreachSearchEndpoint:
    def test_short_query_returns_400(self, client):
        response = client.get("/api/breach-search?q=a")
        assert response.status_code == 400

    def test_empty_query_returns_400(self, client):
        response = client.get("/api/breach-search?q=")
        assert response.status_code == 400


class TestLLMEndpoints:
    def test_llm_status_returns_structure(self, client):
        response = client.get("/api/llm/status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data

    @patch("breachalpha.llm_integration.analyze_breach_dataset", return_value=None)
    def test_llm_analyze_returns_503_when_unavailable(self, mock_analyze, client):
        response = client.post("/api/llm/analyze-dataset", json={
            "dataset_summary": "test",
            "analysis_results": "test",
        })
        assert response.status_code == 503

    @patch("breachalpha.llm_integration.generate_risk_summary", return_value=None)
    def test_llm_risk_summary_returns_503_when_unavailable(self, mock_summary, client):
        response = client.post("/api/llm/risk-summary", json={
            "company": "Test", "risk_score": 50,
            "prediction": "medium", "features": {},
        })
        assert response.status_code == 503


class TestUploadEndpoint:
    def test_upload_csv(self, client, tmp_path):
        import pandas as pd
        csv = tmp_path / "test.csv"
        pd.DataFrame({
            "Company": ["Equifax", "Capital One"],
            "Date": ["2017-09-07", "2019-07-29"],
            "Records": [147000000, 106000000],
        }).to_csv(csv, index=False)

        with open(csv, "rb") as f:
            response = client.post("/api/upload", files={"file": ("test.csv", f, "text/csv")})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["original_rows"] == 2

    def test_upload_unsupported_type(self, client):
        response = client.post("/api/upload", files={"file": ("test.json", b"{}", "application/json")})
        assert response.status_code == 400

    def test_upload_xlsx(self, client, tmp_path):
        import pandas as pd
        xlsx = tmp_path / "test.xlsx"
        pd.DataFrame({
            "Company": ["TestCorp"],
            "Date": ["2024-01-01"],
            "Records": [1000],
        }).to_excel(xlsx, index=False)

        with open(xlsx, "rb") as f:
            response = client.post("/api/upload", files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestExplainEndpoint:
    def test_explain_unknown_company_returns_404(self, client):
        response = client.post("/api/explain", json={
            "company": "FakeCompany999",
            "breach_date": "2024-01-01",
        })
        assert response.status_code == 404

    def test_explain_missing_fields_returns_422(self, client):
        response = client.post("/api/explain", json={})
        assert response.status_code == 422

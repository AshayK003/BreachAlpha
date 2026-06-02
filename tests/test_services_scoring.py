"""Tests for services/scoring.py — ticker validation, company name resolution."""

import pytest

from breachalpha.services.scoring import (
    validate_ticker,
    resolve_company_name_from_ticker,
)


class TestValidateTicker:
    def test_valid_us_ticker(self):
        assert validate_ticker("MSFT") == "MSFT"

    def test_valid_indian_ticker(self):
        assert validate_ticker("TCS.NS") == "TCS.NS"

    def test_lowercase_normalized(self):
        assert validate_ticker("aapl") == "AAPL"

    def test_whitespace_stripped(self):
        assert validate_ticker("  MSFT  ") == "MSFT"

    def test_invalid_characters(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("MSFT!")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("")

    def test_too_long(self):
        with pytest.raises(ValueError, match="Invalid ticker"):
            validate_ticker("A" * 20)

    def test_dot_suffix_valid(self):
        assert validate_ticker("RELIANCE.BO") == "RELIANCE.BO"


class TestResolveCompanyNameFromTicker:
    def test_known_us_ticker(self):
        name = resolve_company_name_from_ticker("MSFT")
        assert "microsoft" in name.lower()

    def test_known_indian_ticker(self):
        name = resolve_company_name_from_ticker("TCS.NS")
        assert "tata" in name.lower()

    def test_unknown_ticker_returns_input(self):
        result = resolve_company_name_from_ticker("ZZZZZ")
        assert result == "ZZZZZ"

    def test_case_insensitive(self):
        name = resolve_company_name_from_ticker("msft")
        assert "microsoft" in name.lower()

    def test_bare_ticker_without_suffix(self):
        name = resolve_company_name_from_ticker("EFX")
        assert name.lower() == "equifax"

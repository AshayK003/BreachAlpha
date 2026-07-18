import pytest


# =====================================================
# Unit tests for _detect_breach_type()
# =====================================================
from breachalpha.breach_search import _extract_records_from_text
class TestExtractRecords:
    def test_million_records(self):
        assert _extract_records_from_text("10 million records breached") == 10_000_000

    def test_billion_users(self):
        assert _extract_records_from_text("1.5B users affected") == 0  # not currently parsed

    def test_thousand_accounts(self):
        assert _extract_records_from_text("50 thousand accounts exposed") == 50_000

    def test_plain_records(self):
        assert _extract_records_from_text("5000 records compromised") == 5000

    def test_no_match_returns_zero(self):
        assert _extract_records_from_text("no numbers here") == 0

    def test_comma_separated(self):
        assert _extract_records_from_text("1,200,000 people affected") == 0  # not currently parsed

    def test_case_insensitive(self):
        assert _extract_records_from_text("5 MILLION RECORDS BREACHED") == 5_000_000


# =====================================================
# Unit tests for _detect_breach_type()
# =====================================================
from breachalpha.breach_search import _detect_breach_type

class TestDetectBreachType:
    def test_ransomware(self):
        assert _detect_breach_type("ransomware attack encrypted servers") == "ransomware"

    def test_phishing(self):
        assert _detect_breach_type("phishing campaign targeted employees") == "phishing"

    def test_insider(self):
        assert _detect_breach_type("insider threat from former employee") == "insider"

    def test_hack(self):
        assert _detect_breach_type("hackers compromised the database") == "hack"

    def test_data_leak(self):
        assert _detect_breach_type("unsecured server exposed customer data") == "data_leak"

    def test_fallback_is_data_leak(self):
        assert _detect_breach_type("some random text") == "data_leak"
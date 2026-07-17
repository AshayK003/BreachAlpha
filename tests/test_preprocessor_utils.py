import pandas as pd
import pytest

# =====================================================
# Tests for _sanitize_formula_injection()
# =====================================================

from breachalpha.preprocessor import _sanitize_formula_injection

class TestSanitizeFormulaInjection:
    def test_formula_equals_prefixed(self):
        df = pd.DataFrame({"col": ["=cmd|' /C calc'!A0", "normal"]})

        _sanitize_formula_injection(df)

        assert df["col"][0].startswith("\t")
        assert df["col"][1] == "normal"

    def test_formula_plus_prefixed(self):
        df = pd.DataFrame({"col": ["+cmd|' /C calc'!A0"]})

        _sanitize_formula_injection(df)

        assert df["col"][0].startswith("\t")

    def test_formula_minus_prefixed(self):
        df = pd.DataFrame({"col": ["-SUM(A1:A10)"]})

        _sanitize_formula_injection(df)

        assert df["col"][0].startswith("\t")

    def test_formula_at_prefixed(self):
        df = pd.DataFrame({"col": ["@SUM(A1:A10)"]})

        _sanitize_formula_injection(df)

        assert df["col"][0].startswith("\t")

    def test_non_string_columns_skipped(self):
        df = pd.DataFrame({"num": [1, 2, 3]})

        _sanitize_formula_injection(df)

        assert list(df["num"]) == [1, 2, 3]

    def test_already_clean_unchanged(self):
        df = pd.DataFrame({"col": ["hello", "world"]})

        _sanitize_formula_injection(df)

        assert list(df["col"]) == ["hello", "world"]

    def test_empty_dataframe(self):
        df = pd.DataFrame({"col": pd.Series([], dtype=object)})

        _sanitize_formula_injection(df)

        assert len(df) == 0



# =====================================================
# Tests for normalize_column_name()
# =====================================================


from breachalpha.preprocessor import normalize_column_name

class TestNormalizeColumnName:
    def test_lowercase(self):
        assert normalize_column_name("Company") == "company"

    def test_spaces_to_underscores(self):
        assert normalize_column_name("First Name") == "first_name"

    def test_hyphens_to_underscores(self):
        assert normalize_column_name("breach-date") == "breach_date"

    def test_special_chars_removed(self):
        assert normalize_column_name("Records (#)") == "records"

    def test_leading_trailing_underscores_stripped(self):
        assert normalize_column_name("_private_") == "private"

    def test_multiple_underscores_collapsed(self):
        assert normalize_column_name("a___b") == "a_b"

    def test_already_normalized(self):
        assert normalize_column_name("company_name") == "company_name"

    def test_empty_string(self):
        assert normalize_column_name("") == ""

    def test_numbers_preserved(self):
        assert normalize_column_name("col123") == "col123"

    def test_dots_removed(self):
        assert normalize_column_name("user.name") == "username"
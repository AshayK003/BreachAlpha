import pandas as pd
import pytest

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
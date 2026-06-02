"""Domain exceptions for BreachAlpha.

Services raise these. Routes translate them to HTTP responses.
This keeps the service layer framework-agnostic.
"""

from __future__ import annotations


class BreachAlphaError(Exception):
    """Base exception for all domain errors."""


class TickerResolutionError(BreachAlphaError):
    """Could not resolve company name to a stock ticker."""

    def __init__(self, company: str):
        self.company = company
        super().__init__(f"Could not resolve ticker for '{company}'")


class InvalidTickerError(BreachAlphaError):
    """Ticker format is invalid."""

    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Invalid ticker format: '{ticker}'")


class InsufficientDataError(BreachAlphaError):
    """Not enough stock data around the breach date to compute features."""

    def __init__(self, company: str, breach_date: str = ""):
        self.company = company
        self.breach_date = breach_date
        detail = f"Insufficient data for {company}"
        if breach_date:
            detail += f" around {breach_date}"
        super().__init__(detail)


class NoStockDataError(BreachAlphaError):
    """No stock data available for the given ticker."""

    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"No stock data available for {ticker}")


class UnsupportedFileTypeError(BreachAlphaError):
    """Uploaded file type is not allowed."""

    def __init__(self, suffix: str, allowed: set[str]):
        self.suffix = suffix
        self.allowed = allowed
        super().__init__(f"Unsupported file type: {suffix}. Allowed: {', '.join(sorted(allowed))}")


class FileTooLargeError(BreachAlphaError):
    """Uploaded file exceeds the size limit."""

    def __init__(self, max_mb: int):
        self.max_mb = max_mb
        super().__init__(f"File too large. Maximum upload size is {max_mb} MB.")


class LLMUnavailableError(BreachAlphaError):
    """LM Studio is not reachable or not responding."""

    def __init__(self, detail: str = "LLM unavailable. Check BREACHALPHA_LLM_URL env var."):
        super().__init__(detail)


class TrainingError(BreachAlphaError):
    """Model training failed."""

    def __init__(self, reason: str):
        super().__init__(f"Training failed: {reason}")

"""Tests for the Tesla Connect Pakistan API re-exports."""

from __future__ import annotations

from custom_components.tesla_connect_pakistan.api import (
    TOKEN_MAX_AGE,
    TeslaConnectApi,
    TeslaConnectApiError,
    TeslaConnectAuthError,
)


class TestApiReExports:
    """Verify that the api module correctly re-exports from pyteslaconnectpk."""

    def test_api_class_available(self) -> None:
        """TeslaConnectApi should be importable from the api module."""
        assert TeslaConnectApi is not None

    def test_auth_error_available(self) -> None:
        """TeslaConnectAuthError should be importable from the api module."""
        assert issubclass(TeslaConnectAuthError, Exception)

    def test_api_error_available(self) -> None:
        """TeslaConnectApiError should be importable from the api module."""
        assert issubclass(TeslaConnectApiError, Exception)

    def test_token_max_age_is_int(self) -> None:
        """TOKEN_MAX_AGE should be a positive integer."""
        assert isinstance(TOKEN_MAX_AGE, int)
        assert TOKEN_MAX_AGE > 0

    def test_api_class_is_from_library(self) -> None:
        """TeslaConnectApi should originate from the pyteslaconnectpk package."""
        assert TeslaConnectApi.__module__ == "pyteslaconnectpk.client"

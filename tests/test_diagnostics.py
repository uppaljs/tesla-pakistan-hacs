"""Tests for Tesla Connect Pakistan diagnostics."""

from __future__ import annotations

from custom_components.tesla_connect_pakistan.diagnostics import TO_REDACT

from .conftest import MOCK_CONFIG_ENTRY_DATA


class TestDiagnosticsRedaction:
    """Tests for sensitive data redaction in diagnostics."""

    def test_redact_list_includes_password(self) -> None:
        """Password should be in the redaction list."""
        assert "password" in TO_REDACT

    def test_redact_list_includes_phone(self) -> None:
        """Phone number should be in the redaction list."""
        assert "phone" in TO_REDACT

    def test_redact_list_includes_token(self) -> None:
        """Token should be in the redaction list."""
        assert "token" in TO_REDACT

    def test_config_entry_data_has_sensitive_fields(self) -> None:
        """Config entry data should contain fields that need redaction."""
        assert "password" in MOCK_CONFIG_ENTRY_DATA
        assert "phone" in MOCK_CONFIG_ENTRY_DATA

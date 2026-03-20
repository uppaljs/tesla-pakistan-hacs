"""Tests for the Tesla Connect Pakistan config flow."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from custom_components.tesla_connect_pakistan.api import (
    TeslaConnectApiError,
    TeslaConnectAuthError,
)
from custom_components.tesla_connect_pakistan.const import (
    CONF_PASSWORD,
    CONF_PHONE,
    DOMAIN,
)

from .conftest import MOCK_CONFIG_ENTRY_DATA, MOCK_PASSWORD, MOCK_PHONE, MOCK_USER_NAME


@pytest.fixture
def mock_sign_in_success() -> MagicMock:
    """Patch sign_in to succeed."""
    with patch(
        "custom_components.tesla_connect_pakistan.config_flow.TeslaConnectApi",
    ) as mock_cls:
        api = mock_cls.return_value
        api.user_name = MOCK_USER_NAME
        api.sign_in.return_value = None
        yield mock_cls


@pytest.fixture
def mock_sign_in_auth_error() -> MagicMock:
    """Patch sign_in to raise an auth error."""
    with patch(
        "custom_components.tesla_connect_pakistan.config_flow.TeslaConnectApi",
    ) as mock_cls:
        api = mock_cls.return_value
        api.sign_in.side_effect = TeslaConnectAuthError("bad credentials")
        yield mock_cls


@pytest.fixture
def mock_sign_in_api_error() -> MagicMock:
    """Patch sign_in to raise a connection error."""
    with patch(
        "custom_components.tesla_connect_pakistan.config_flow.TeslaConnectApi",
    ) as mock_cls:
        api = mock_cls.return_value
        api.sign_in.side_effect = TeslaConnectApiError("connection refused")
        yield mock_cls


class TestConfigFlow:
    """Tests for TeslaConnectConfigFlow."""

    async def test_user_step_shows_form(self, hass) -> None:
        """The user step should show the phone/password form."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert CONF_PHONE in result["data_schema"].schema
        assert CONF_PASSWORD in result["data_schema"].schema

    async def test_user_step_success(self, hass, mock_sign_in_success) -> None:
        """Valid credentials should create a config entry."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=MOCK_CONFIG_ENTRY_DATA,
        )
        assert result["type"] == "create_entry"
        assert result["title"] == f"Tesla Connect ({MOCK_USER_NAME})"
        assert result["data"][CONF_PHONE] == MOCK_PHONE
        assert result["data"][CONF_PASSWORD] == MOCK_PASSWORD

    async def test_user_step_invalid_auth(
        self, hass, mock_sign_in_auth_error
    ) -> None:
        """Invalid credentials should show an auth error."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=MOCK_CONFIG_ENTRY_DATA,
        )
        assert result["type"] == "form"
        assert result["errors"] == {"base": "invalid_auth"}

    async def test_user_step_cannot_connect(
        self, hass, mock_sign_in_api_error
    ) -> None:
        """Connection failures should show a connect error."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=MOCK_CONFIG_ENTRY_DATA,
        )
        assert result["type"] == "form"
        assert result["errors"] == {"base": "cannot_connect"}

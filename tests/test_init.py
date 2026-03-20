"""Tests for Tesla Connect Pakistan integration setup and teardown."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from custom_components.tesla_connect_pakistan.const import DOMAIN

from .conftest import MOCK_CONFIG_ENTRY_DATA, MOCK_SIGN_IN_RESPONSE


class TestSetupEntry:
    """Tests for async_setup_entry and async_unload_entry."""

    async def test_setup_creates_coordinator(self, hass, mock_api) -> None:
        """Setting up an entry should register a coordinator in hass.data."""
        with patch(
            "custom_components.tesla_connect_pakistan.TeslaConnectApi",
            return_value=mock_api,
        ):
            entry = _create_mock_entry(hass)
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()

            assert DOMAIN in hass.data
            assert entry.entry_id in hass.data[DOMAIN]

    async def test_unload_removes_coordinator(self, hass, mock_api) -> None:
        """Unloading an entry should remove it from hass.data."""
        with patch(
            "custom_components.tesla_connect_pakistan.TeslaConnectApi",
            return_value=mock_api,
        ):
            entry = _create_mock_entry(hass)
            await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()

            await hass.config_entries.async_unload(entry.entry_id)
            await hass.async_block_till_done()

            assert entry.entry_id not in hass.data.get(DOMAIN, {})


def _create_mock_entry(hass):
    """Create and add a mock config entry."""
    from homeassistant.config_entries import ConfigEntry

    entry = ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Tesla Connect (Test)",
        data=MOCK_CONFIG_ENTRY_DATA,
        source="user",
        unique_id="03001234567",
    )
    entry.add_to_hass(hass)
    return entry

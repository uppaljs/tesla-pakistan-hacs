"""DataUpdateCoordinator for Tesla Connect Pakistan."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TeslaConnectApi, TeslaConnectApiError, TeslaConnectAuthError
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DEVICE_TYPE_GEYSER,
    DEVICE_TYPE_INVERTER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class TeslaConnectCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches data for all devices on a single account."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, api: TeslaConnectApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll every device and return a dict keyed by device_id."""
        try:
            # Ensure we have a valid token (re-login if expired).
            # This also refreshes self.api.devices.
            if self.api.token_expired:
                await self.hass.async_add_executor_job(self.api.sign_in)

            result: dict[str, Any] = {}

            for device in self.api.devices:
                did = device["device_id"]
                name = device.get("name", "")
                type_id = device.get("type_id", 0)

                try:
                    if type_id == DEVICE_TYPE_GEYSER:
                        details = await self.hass.async_add_executor_job(
                            self.api.get_geyser_details, did, name
                        )
                    elif type_id == DEVICE_TYPE_INVERTER:
                        details = await self.hass.async_add_executor_job(
                            self.api.get_inverter_details, did, name
                        )
                    else:
                        details = {}
                except TeslaConnectApiError as exc:
                    _LOGGER.warning("Failed to fetch %s (%s): %s", name, did, exc)
                    details = {}

                result[did] = {
                    "device": device,
                    "details": details,
                    "type_id": type_id,
                }

            return result

        except TeslaConnectAuthError as exc:
            raise UpdateFailed(f"Authentication failed: {exc}") from exc
        except TeslaConnectApiError as exc:
            raise UpdateFailed(f"API error: {exc}") from exc

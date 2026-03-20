"""DataUpdateCoordinator for the Tesla Connect Pakistan integration."""

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
    """Coordinator that fetches data for all devices on a single account."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: TeslaConnectApi,
        entry: ConfigEntry,
    ) -> None:
        """Initialise the coordinator with a shared API client.

        Args:
            hass: The Home Assistant instance.
            api: An authenticated TeslaConnectApi client.
            entry: The config entry, used to read options like scan interval.

        """
        scan_interval: int = entry.options.get(
            "scan_interval", DEFAULT_SCAN_INTERVAL
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll every registered device and return a mapping keyed by device_id.

        Re-authenticates transparently when the token has expired before
        issuing per-device detail requests.  Individual device failures are
        logged and silently replaced with an empty details dict so that a
        single unreachable device does not abort the entire update cycle.

        Returns:
            A dict whose keys are device_id strings.  Each value is a dict
            with the keys ``device``, ``details``, and ``type_id``.

        Raises:
            UpdateFailed: When authentication fails or an API-level error
                prevents the device list from being fetched.

        """
        try:
            # Re-login when the token has expired; this also refreshes
            # self.api.devices with the current device list from the server
            if self.api.token_expired:
                await self.hass.async_add_executor_job(self.api.sign_in)

            result: dict[str, Any] = {}

            for device in self.api.devices:
                did: str = device["device_id"]
                name: str = device.get("name", "")
                type_id: int = device.get("type_id", 0)
                details: dict[str, Any]

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
                    _LOGGER.warning(
                        "Failed to fetch details for %s (%s): %s", name, did, exc
                    )
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

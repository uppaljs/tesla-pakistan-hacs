"""Support for Tesla Connect Pakistan geyser and inverter devices."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .api import TeslaConnectApi, TeslaConnectApiError, TeslaConnectAuthError
from .const import CONF_PASSWORD, CONF_PHONE, DOMAIN
from .coordinator import TeslaConnectCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tesla Connect Pakistan from a config entry.

    Raises:
        ConfigEntryAuthFailed: When credentials are invalid or expired,
            triggering the reauth flow automatically.
        ConfigEntryNotReady: When the API is temporarily unreachable,
            causing HA to retry setup automatically.

    """
    api = TeslaConnectApi(
        phone=entry.data[CONF_PHONE],
        password=entry.data[CONF_PASSWORD],
    )

    # Perform the initial login to obtain a token and the device list.
    # Auth failures trigger reauth; connection failures trigger retry.
    try:
        await hass.async_add_executor_job(api.sign_in)
    except TeslaConnectAuthError as err:
        raise ConfigEntryAuthFailed(err) from err
    except TeslaConnectApiError as err:
        raise ConfigEntryNotReady(err) from err

    coordinator = TeslaConnectCoordinator(hass, api, entry)

    # First refresh — raises ConfigEntryNotReady on failure, or
    # ConfigEntryAuthFailed if the coordinator encounters an auth error.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Tesla Connect Pakistan config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

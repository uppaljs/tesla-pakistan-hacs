"""Diagnostics support for the Tesla Connect Pakistan integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import CONF_PASSWORD, CONF_PHONE, DOMAIN
from .coordinator import TeslaConnectCoordinator

# Fields to redact from diagnostics output.
TO_REDACT = {CONF_PASSWORD, CONF_PHONE, "phone", "token"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Includes redacted config data, current options, and the full
    coordinator data snapshot for all devices.
    """
    coordinator: TeslaConnectCoordinator = entry.runtime_data.coordinator

    device_diagnostics: dict[str, Any] = {}
    if coordinator.data:
        for device_id, data in coordinator.data.items():
            device_diagnostics[device_id] = {
                "device": async_redact_data(data.get("device", {}), TO_REDACT),
                "details": async_redact_data(data.get("details", {}), TO_REDACT),
                "type_id": data.get("type_id"),
            }

    return {
        "config_entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": dict(entry.options),
            "unique_id": entry.unique_id,
            "version": entry.version,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
        },
        "devices": device_diagnostics,
        "api": {
            "token_expired": coordinator.api.token_expired,
            "user_name": coordinator.api.user_name,
        },
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a specific device.

    Locates the device by matching its identifier against the
    coordinator data and returns the redacted detail payload.
    """
    coordinator: TeslaConnectCoordinator = entry.runtime_data.coordinator

    # Extract the device_id from the device registry identifiers.
    device_id: str | None = None
    for identifier in device.identifiers:
        if identifier[0] == DOMAIN:
            device_id = identifier[1]
            break

    if device_id is None or not coordinator.data:
        return {"error": "Device not found in coordinator data"}

    data = coordinator.data.get(device_id, {})
    return {
        "device": async_redact_data(data.get("device", {}), TO_REDACT),
        "details": async_redact_data(data.get("details", {}), TO_REDACT),
        "type_id": data.get("type_id"),
    }

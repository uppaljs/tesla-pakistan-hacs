"""System health support for the Tesla Connect Pakistan integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import BASE_URL, DOMAIN
from .coordinator import TeslaConnectCoordinator


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register system health callbacks."""
    register.async_register_info(system_health_info)


async def system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Get system health info for the Tesla Connect Pakistan integration."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return {"api_endpoint": BASE_URL}

    entry = entries[0]
    coordinator: TeslaConnectCoordinator = entry.runtime_data.coordinator

    device_count = len(coordinator.api.devices) if coordinator.api.devices else 0

    return {
        "api_endpoint": BASE_URL,
        "authenticated_user": coordinator.api.user_name or "Unknown",
        "can_reach_server": system_health.async_check_can_reach_url(hass, BASE_URL),
        "devices": device_count,
        "token_valid": not coordinator.api.token_expired,
    }

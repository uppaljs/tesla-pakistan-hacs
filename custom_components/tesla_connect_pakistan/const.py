"""Constants for the Tesla Connect Pakistan integration."""

from __future__ import annotations

from pyteslaconnectpk import (  # noqa: F401
    BASE_URL,
    DEVICE_TYPE_GEYSER,
    DEVICE_TYPE_INVERTER,
    GEYSER_MODE_AUTOMATIC,
    GEYSER_MODE_ELECTRICITY,
    GEYSER_MODE_GAS,
    GEYSER_MODE_SOLAR_DISABLED,
    GEYSER_MODE_SOLAR_ENABLED,
    STATUS_OFF,
    STATUS_ON,
)

# Integration identity.
DOMAIN: str = "tesla_connect_pakistan"
MANUFACTURER: str = "Tesla Tech Pakistan"

# --- Configuration entry keys ---

CONF_PASSWORD: str = "password"
CONF_PHONE: str = "phone"

# --- Geyser mode mappings (HA-specific) ---

# Mapping from API integer mode value to Home Assistant operation mode string.
GEYSER_MODES: dict[int, str] = {
    GEYSER_MODE_AUTOMATIC: "auto",
    GEYSER_MODE_ELECTRICITY: "electric",
    GEYSER_MODE_GAS: "gas",
    GEYSER_MODE_SOLAR_DISABLED: "solar_off",
    GEYSER_MODE_SOLAR_ENABLED: "solar_on",
}

# Reverse mapping from Home Assistant operation mode string to API integer.
GEYSER_MODES_REVERSE: dict[str, int] = {v: k for k, v in GEYSER_MODES.items()}

# --- Options flow keys ---

CONF_ENABLE_SCHEDULE_SWITCHES: str = "enable_schedule_switches"
CONF_SCAN_INTERVAL: str = "scan_interval"

# --- Polling ---

# Default coordinator update interval in seconds.
DEFAULT_SCAN_INTERVAL: int = 30

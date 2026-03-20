"""Constants for the Tesla Connect Pakistan integration."""

from __future__ import annotations

# Integration identity.
DOMAIN: str = "tesla_connect_pakistan"
MANUFACTURER: str = "Tesla Tech Pakistan"

# --- API ---

# Base URL for the Tesla Tech Pakistan cloud API.
API_AUTH_KEY: str = "146ngU0W4Hx0aahiyYShehO7ARo5XPhCJcT"
BASE_URL: str = "https://api.tesla-tech.com/"
OKHTTP_UA: str = "okhttp/4.12.0"

# --- Configuration entry keys ---

CONF_PASSWORD: str = "password"
CONF_PHONE: str = "phone"

# --- Device types (from the DeviceType enum) ---

DEVICE_TYPE_GEYSER: int = 2
DEVICE_TYPE_INVERTER: int = 1

# --- Geyser operation modes (from the GeyserMode enum) ---

GEYSER_MODE_AUTOMATIC: int = 2
GEYSER_MODE_ELECTRICITY: int = 1
GEYSER_MODE_GAS: int = 0
GEYSER_MODE_SOLAR_DISABLED: int = 4
GEYSER_MODE_SOLAR_ENABLED: int = 3

# Mapping from API integer mode value to Home Assistant operation mode string.
GEYSER_MODES: dict[int, str] = {
    GEYSER_MODE_AUTOMATIC: "auto",
    GEYSER_MODE_ELECTRICITY: "electric",
    GEYSER_MODE_GAS: "gas",
    GEYSER_MODE_SOLAR_DISABLED: "solar_off",
    GEYSER_MODE_SOLAR_ENABLED: "solar_on",
}

# Reverse mapping from Home Assistant operation mode string to API integer mode value.
GEYSER_MODES_REVERSE: dict[str, int] = {v: k for k, v in GEYSER_MODES.items()}

# --- Device status values (from the Status enum) ---

STATUS_OFF: int = 0
STATUS_ON: int = 1

# --- Polling ---

# Default coordinator update interval in seconds.
DEFAULT_SCAN_INTERVAL: int = 30

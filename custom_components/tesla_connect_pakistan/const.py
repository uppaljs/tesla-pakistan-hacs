"""Constants for the Tesla Connect Pakistan integration."""

DOMAIN = "tesla_connect_pakistan"
MANUFACTURER = "Tesla Tech Pakistan"

# API
BASE_URL = "https://api.tesla-tech.com/"
API_AUTH_KEY = "146ngU0W4Hx0aahiyYShehO7ARo5XPhCJcT"
OKHTTP_UA = "okhttp/4.12.0"

# Config
CONF_PHONE = "phone"
CONF_PASSWORD = "password"

# Polling
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Device types (from DeviceType enum)
DEVICE_TYPE_INVERTER = 1
DEVICE_TYPE_GEYSER = 2

# Geyser modes (from GeyserMode enum)
GEYSER_MODE_GAS = 0
GEYSER_MODE_ELECTRICITY = 1
GEYSER_MODE_AUTOMATIC = 2
GEYSER_MODE_SOLAR_ENABLED = 3
GEYSER_MODE_SOLAR_DISABLED = 4

GEYSER_MODES = {
    GEYSER_MODE_GAS: "gas",
    GEYSER_MODE_ELECTRICITY: "electric",
    GEYSER_MODE_AUTOMATIC: "auto",
    GEYSER_MODE_SOLAR_ENABLED: "solar_on",
    GEYSER_MODE_SOLAR_DISABLED: "solar_off",
}

GEYSER_MODES_REVERSE = {v: k for k, v in GEYSER_MODES.items()}

# Status (from Status enum)
STATUS_ON = 1
STATUS_OFF = 0

# HA water_heater operation modes
HA_MODE_MAP = {
    "gas": GEYSER_MODE_GAS,
    "electric": GEYSER_MODE_ELECTRICITY,
    "auto": GEYSER_MODE_AUTOMATIC,
    "solar_on": GEYSER_MODE_SOLAR_ENABLED,
    "solar_off": GEYSER_MODE_SOLAR_DISABLED,
}

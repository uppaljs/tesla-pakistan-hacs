"""Test fixtures for the Tesla Connect Pakistan integration."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from custom_components.tesla_connect_pakistan.const import (
    CONF_PASSWORD,
    CONF_PHONE,
    DOMAIN,
)

MOCK_PHONE = "03001234567"
MOCK_PASSWORD = "testpass123"
MOCK_TOKEN = "dGVzdHRva2VuMTIz"
MOCK_USER_NAME = "Test User"

MOCK_GEYSER_DEVICE: dict[str, Any] = {
    "curr_temp": 46,
    "device_id": "test_geyser_001",
    "energy_day": 0,
    "image": "images/X-Gen.png",
    "model_id": 1,
    "name": "Test Geyser",
    "online": True,
    "savings": 0,
    "type_id": 2,
}

MOCK_INVERTER_DEVICE: dict[str, Any] = {
    "curr_temp": 0,
    "device_id": "test_inverter_001",
    "energy_day": 1500,
    "image": "images/inverter.png",
    "model_id": 8,
    "name": "Test Inverter",
    "online": True,
    "savings": 100,
    "type_id": 1,
}

MOCK_SIGN_IN_RESPONSE: dict[str, Any] = {
    "devices": [MOCK_GEYSER_DEVICE, MOCK_INVERTER_DEVICE],
    "name": MOCK_USER_NAME,
    "phone": MOCK_PHONE.lstrip("0"),
    "status": "Success",
    "token": MOCK_TOKEN,
}

MOCK_GEYSER_DETAILS: dict[str, Any] = {
    "boost": 0,
    "burner": 1,
    "curr_mode": 0,
    "curr_temp": 46,
    "device_id": "test_geyser_001",
    "electric_units": 3828000,
    "gas_units": 4661,
    "solar": 0,
    "status": "Success",
    "status_label": "Currently Using Gas",
    "temp_label": "Heating up to 50 degrees",
    "temp_limit": 50,
    "times": [
        {"status": False, "time": "0:00 - 0:59"},
        {"status": False, "time": "1:00 - 1:59"},
        {"status": False, "time": "2:00 - 2:59"},
        {"status": False, "time": "3:00 - 3:59"},
        {"status": True, "time": "4:00 - 4:59"},
        {"status": True, "time": "5:00 - 5:59"},
        {"status": True, "time": "6:00 - 6:59"},
        {"status": True, "time": "7:00 - 7:59"},
        {"status": True, "time": "8:00 - 8:59"},
        {"status": True, "time": "9:00 - 9:59"},
        {"status": True, "time": "10:00 - 10:59"},
        {"status": True, "time": "11:00 - 11:59"},
        {"status": True, "time": "12:00 - 12:59"},
        {"status": True, "time": "13:00 - 13:59"},
        {"status": True, "time": "14:00 - 14:59"},
        {"status": True, "time": "15:00 - 15:59"},
        {"status": True, "time": "16:00 - 16:59"},
        {"status": True, "time": "17:00 - 17:59"},
        {"status": True, "time": "18:00 - 18:59"},
        {"status": True, "time": "19:00 - 19:59"},
        {"status": True, "time": "20:00 - 20:59"},
        {"status": True, "time": "21:00 - 21:59"},
        {"status": True, "time": "22:00 - 22:59"},
        {"status": True, "time": "23:00 - 23:59"},
    ],
    "two_hour_mode": 0,
    "user_mode": 2,
    "vacation": 0,
}

MOCK_INVERTER_DETAILS: dict[str, Any] = {
    "battery_direction": 0,
    "battery_percentage": 85,
    "battery_voltage": 52,
    "device_id": "test_inverter_001",
    "energy_day": 1500,
    "energy_month": 225500,
    "energy_total": 4756000,
    "energy_week": 228355,
    "energy_year": 0,
    "faults": 0,
    "grid_status": 1,
    "savings_day": 1824,
    "savings_week": 7775,
    "solar_status": 1,
    "status": "Success",
}

MOCK_CONFIG_ENTRY_DATA: dict[str, str] = {
    CONF_PASSWORD: MOCK_PASSWORD,
    CONF_PHONE: MOCK_PHONE,
}


@pytest.fixture
def mock_api() -> Generator[MagicMock]:
    """Return a mocked TeslaConnectApi instance."""
    with patch(
        "custom_components.tesla_connect_pakistan.api.TeslaConnectApi",
        autospec=True,
    ) as mock_cls:
        api = mock_cls.return_value
        api.token = MOCK_TOKEN
        api.token_expired = False
        api.user_name = MOCK_USER_NAME
        api.phone = MOCK_PHONE
        api.devices = [MOCK_GEYSER_DEVICE, MOCK_INVERTER_DEVICE]
        api.sign_in.return_value = MOCK_SIGN_IN_RESPONSE
        api.get_geyser_details.return_value = MOCK_GEYSER_DETAILS
        api.get_inverter_details.return_value = MOCK_INVERTER_DETAILS
        api.set_geyser_boost.return_value = MOCK_GEYSER_DETAILS
        api.set_geyser_mode.return_value = MOCK_GEYSER_DETAILS
        api.set_geyser_temp_limit.return_value = MOCK_GEYSER_DETAILS
        api.set_geyser_timer.return_value = MOCK_GEYSER_DETAILS
        api.set_geyser_two_hour_mode.return_value = MOCK_GEYSER_DETAILS
        api.set_geyser_vacation_mode.return_value = MOCK_GEYSER_DETAILS
        yield api

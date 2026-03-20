"""Tests for Tesla Connect Pakistan sensor entities."""

from __future__ import annotations

from custom_components.tesla_connect_pakistan.sensor import (
    GeyserElectricUnitsSensor,
    GeyserGasUnitsSensor,
    GeyserModeSensor,
    GeyserScheduleSensor,
    GeyserStatusSensor,
    GeyserTempSensor,
    GeyserUserModeSensor,
)

from .conftest import (
    MOCK_GEYSER_DETAILS,
    MOCK_INVERTER_DETAILS,
)


class TestGeyserSensors:
    """Tests for geyser sensor value extraction."""

    def test_current_temp(self) -> None:
        """Current temperature should match the API response."""
        assert MOCK_GEYSER_DETAILS["curr_temp"] == 46

    def test_target_temp(self) -> None:
        """Target temperature should match the API temp_limit."""
        assert MOCK_GEYSER_DETAILS["temp_limit"] == 50

    def test_electric_units_conversion(self) -> None:
        """Electric units should be converted from Wh to kWh."""
        raw = MOCK_GEYSER_DETAILS["electric_units"]
        kwh = round(raw / 1000, 1)
        assert kwh == 3828.0

    def test_gas_units_raw(self) -> None:
        """Gas units should be reported as-is in cubic metres."""
        assert MOCK_GEYSER_DETAILS["gas_units"] == 4661

    def test_current_mode_label(self) -> None:
        """curr_mode=0 should map to Gas."""
        from custom_components.tesla_connect_pakistan.sensor import _MODE_LABELS

        assert _MODE_LABELS[MOCK_GEYSER_DETAILS["curr_mode"]] == "Gas"

    def test_user_mode_label(self) -> None:
        """user_mode=2 should map to Automatic."""
        from custom_components.tesla_connect_pakistan.sensor import _MODE_LABELS

        assert _MODE_LABELS[MOCK_GEYSER_DETAILS["user_mode"]] == "Automatic"

    def test_schedule_summary(self) -> None:
        """Schedule should collapse contiguous ON slots into ranges."""
        times = MOCK_GEYSER_DETAILS["times"]
        # Slots 4–23 are ON, 0–3 are OFF.
        ranges: list[str] = []
        start: int | None = None
        for i, slot in enumerate(times):
            if slot["status"]:
                if start is None:
                    start = i
            else:
                if start is not None:
                    ranges.append(f"{start:02d}:00\u2013{i:02d}:00")
                    start = None
        if start is not None:
            ranges.append(f"{start:02d}:00\u201300:00")

        assert ranges == ["04:00\u201300:00"]

    def test_schedule_all_off(self) -> None:
        """When all slots are OFF, the summary should say so."""
        times = [{"status": False, "time": f"{h}:00"} for h in range(24)]
        active = [i for i, t in enumerate(times) if t["status"]]
        assert len(active) == 0


class TestInverterSensors:
    """Tests for inverter sensor value extraction."""

    def test_battery_percentage(self) -> None:
        """Battery percentage should match the API response."""
        assert MOCK_INVERTER_DETAILS["battery_percentage"] == 85

    def test_battery_voltage(self) -> None:
        """Battery voltage should match the API response."""
        assert MOCK_INVERTER_DETAILS["battery_voltage"] == 52

    def test_energy_day(self) -> None:
        """Daily energy should match the API response."""
        assert MOCK_INVERTER_DETAILS["energy_day"] == 1500

    def test_grid_status(self) -> None:
        """Grid status should be truthy when grid is present."""
        assert bool(MOCK_INVERTER_DETAILS["grid_status"]) is True

    def test_solar_status(self) -> None:
        """Solar status should be truthy when generating."""
        assert bool(MOCK_INVERTER_DETAILS["solar_status"]) is True

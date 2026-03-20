"""Sensor platform for Tesla Connect Pakistan."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPE_GEYSER, DEVICE_TYPE_INVERTER, DOMAIN, GEYSER_MODES
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

# Mode display names — friendly labels for HA UI
_MODE_LABELS: dict[int, str] = {
    0: "Gas",
    1: "Electricity",
    2: "Automatic",
    3: "Solar (On)",
    4: "Solar (Off)",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TeslaConnectCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name = device.get("name", did)
        type_id = data["type_id"]

        if type_id == DEVICE_TYPE_GEYSER:
            entities.extend(
                [
                    GeyserTempSensor(coordinator, did, name, type_id),
                    GeyserTargetTempSensor(coordinator, did, name, type_id),
                    GeyserStatusSensor(coordinator, did, name, type_id),
                    GeyserModeSensor(coordinator, did, name, type_id),
                    GeyserUserModeSensor(coordinator, did, name, type_id),
                    GeyserGasUnitsSensor(coordinator, did, name, type_id),
                    GeyserElectricUnitsSensor(coordinator, did, name, type_id),
                    GeyserScheduleSensor(coordinator, did, name, type_id),
                ]
            )
        elif type_id == DEVICE_TYPE_INVERTER:
            entities.extend(
                [
                    InverterBatteryPercentSensor(coordinator, did, name, type_id),
                    InverterBatteryVoltageSensor(coordinator, did, name, type_id),
                    InverterEnergyDaySensor(coordinator, did, name, type_id),
                    InverterEnergyWeekSensor(coordinator, did, name, type_id),
                    InverterEnergyMonthSensor(coordinator, did, name, type_id),
                    InverterEnergyTotalSensor(coordinator, did, name, type_id),
                    InverterSavingsDaySensor(coordinator, did, name, type_id),
                    InverterFaultsSensor(coordinator, did, name, type_id),
                ]
            )

    async_add_entities(entities)


# ── Geyser sensors ───────────────────────────────────────────────────


class GeyserTempSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_current_temp"

    @property
    def name(self) -> str:
        return "Current temperature"

    @property
    def native_value(self) -> float | None:
        return self._details.get("curr_temp")


class GeyserTargetTempSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_target_temp"

    @property
    def name(self) -> str:
        return "Target temperature"

    @property
    def native_value(self) -> float | None:
        return self._details.get("temp_limit")


class GeyserStatusSensor(TeslaConnectEntity, SensorEntity):
    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_status_label"

    @property
    def name(self) -> str:
        return "Status"

    @property
    def native_value(self) -> str | None:
        return self._details.get("status_label")

    @property
    def icon(self) -> str:
        return "mdi:water-boiler"


class GeyserModeSensor(TeslaConnectEntity, SensorEntity):
    """The *actual* operating mode the geyser is currently using.

    In automatic mode the device picks gas or electric based on
    availability, so curr_mode will differ from user_mode.
    """

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_current_mode"

    @property
    def name(self) -> str:
        return "Current mode"

    @property
    def native_value(self) -> str | None:
        mode_val = self._details.get("curr_mode")
        if mode_val is None:
            return None
        return _MODE_LABELS.get(mode_val, str(mode_val))

    @property
    def icon(self) -> str:
        mode_val = self._details.get("curr_mode")
        if mode_val == 0:
            return "mdi:fire"
        if mode_val == 1:
            return "mdi:lightning-bolt"
        if mode_val in (3, 4):
            return "mdi:solar-power"
        return "mdi:auto-fix"


class GeyserUserModeSensor(TeslaConnectEntity, SensorEntity):
    """The mode the user selected (may differ from curr_mode in auto)."""

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_user_mode"

    @property
    def name(self) -> str:
        return "User mode"

    @property
    def native_value(self) -> str | None:
        mode_val = self._details.get("user_mode")
        if mode_val is None:
            return None
        return _MODE_LABELS.get(mode_val, str(mode_val))

    @property
    def icon(self) -> str:
        return "mdi:cog"


class GeyserGasUnitsSensor(TeslaConnectEntity, SensorEntity):
    """Gas consumption in cubic metres (m³)."""

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_device_class = SensorDeviceClass.GAS
    _attr_icon = "mdi:fire-circle"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_gas_units"

    @property
    def name(self) -> str:
        return "Gas consumption"

    @property
    def native_value(self) -> int | None:
        return self._details.get("gas_units")


class GeyserElectricUnitsSensor(TeslaConnectEntity, SensorEntity):
    """Electric consumption in kWh.

    The API returns watts; the app divides by 1000 when > 1000 and
    labels it "kW".  We convert to kWh for HA energy tracking.
    """

    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_suggested_display_precision = 1

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_electric_units"

    @property
    def name(self) -> str:
        return "Electric consumption"

    @property
    def native_value(self) -> float | None:
        raw = self._details.get("electric_units")
        if raw is None:
            return None
        # API value is in Wh; convert to kWh
        return round(raw / 1000, 1)


class GeyserScheduleSensor(TeslaConnectEntity, SensorEntity):
    """Shows the active schedule as a human-readable summary.

    Example: "04:00–23:00 ON" or "04:00–09:00, 16:00–22:00 ON".
    The full 24-slot schedule is available in extra_state_attributes.
    """

    _attr_icon = "mdi:calendar-clock"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_schedule"

    @property
    def name(self) -> str:
        return "Schedule"

    @property
    def native_value(self) -> str | None:
        times = self._details.get("times", [])
        if not times:
            return None

        # Build list of ON ranges
        ranges: list[str] = []
        start: int | None = None
        for i, slot in enumerate(times):
            if slot.get("status"):
                if start is None:
                    start = i
            else:
                if start is not None:
                    ranges.append(f"{start:02d}:00–{i:02d}:00")
                    start = None
        if start is not None:
            ranges.append(f"{start:02d}:00–00:00")

        if not ranges:
            return "All day OFF"
        if len(ranges) == 1 and ranges[0] == "00:00–00:00":
            return "All day ON"
        return ", ".join(ranges)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        times = self._details.get("times", [])
        active = [i for i, t in enumerate(times) if t.get("status")]
        return {
            "active_hours": [f"{h:02d}:00" for h in active],
            "active_count": len(active),
            "total_slots": len(times),
        }


# ── Inverter sensors ─────────────────────────────────────────────────


class InverterBatteryPercentSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_battery_pct"

    @property
    def name(self) -> str:
        return "Battery"

    @property
    def native_value(self) -> int | None:
        return self._details.get("battery_percentage")


class InverterBatteryVoltageSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = "V"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_battery_voltage"

    @property
    def name(self) -> str:
        return "Battery voltage"

    @property
    def native_value(self) -> int | None:
        return self._details.get("battery_voltage")


class InverterEnergyDaySensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_energy_day"

    @property
    def name(self) -> str:
        return "Energy today"

    @property
    def native_value(self) -> int | None:
        return self._details.get("energy_day")


class InverterEnergyWeekSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_energy_week"

    @property
    def name(self) -> str:
        return "Energy this week"

    @property
    def native_value(self) -> int | None:
        return self._details.get("energy_week")


class InverterEnergyMonthSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_energy_month"

    @property
    def name(self) -> str:
        return "Energy this month"

    @property
    def native_value(self) -> int | None:
        return self._details.get("energy_month")


class InverterEnergyTotalSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_energy_total"

    @property
    def name(self) -> str:
        return "Energy total"

    @property
    def native_value(self) -> int | None:
        return self._details.get("energy_total")


class InverterSavingsDaySensor(TeslaConnectEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:piggy-bank"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_savings_day"

    @property
    def name(self) -> str:
        return "Savings today"

    @property
    def native_value(self) -> int | None:
        return self._details.get("savings_day")


class InverterFaultsSensor(TeslaConnectEntity, SensorEntity):
    _attr_icon = "mdi:alert-circle"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_faults"

    @property
    def name(self) -> str:
        return "Faults"

    @property
    def native_value(self) -> int | None:
        return self._details.get("faults")

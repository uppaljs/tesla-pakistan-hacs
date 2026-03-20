"""Sensor platform for the Tesla Connect Pakistan integration."""

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
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPE_GEYSER, DEVICE_TYPE_INVERTER, DOMAIN
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

# Friendly labels for geyser mode integers.
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
    """Set up Tesla Connect sensors from a config entry."""
    coordinator: TeslaConnectCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name: str = device.get("name", did)
        type_id: int = data["type_id"]

        if type_id == DEVICE_TYPE_GEYSER:
            entities.extend(
                [
                    GeyserElectricUnitsSensor(coordinator, did, name, type_id),
                    GeyserGasUnitsSensor(coordinator, did, name, type_id),
                    GeyserModeSensor(coordinator, did, name, type_id),
                    GeyserScheduleSensor(coordinator, did, name, type_id),
                    GeyserStatusSensor(coordinator, did, name, type_id),
                    GeyserTargetTempSensor(coordinator, did, name, type_id),
                    GeyserTempSensor(coordinator, did, name, type_id),
                    GeyserUserModeSensor(coordinator, did, name, type_id),
                ]
            )
        elif type_id == DEVICE_TYPE_INVERTER:
            entities.extend(
                [
                    InverterBatteryPercentSensor(coordinator, did, name, type_id),
                    InverterBatteryVoltageSensor(coordinator, did, name, type_id),
                    InverterEnergyDaySensor(coordinator, did, name, type_id),
                    InverterEnergyMonthSensor(coordinator, did, name, type_id),
                    InverterEnergyTotalSensor(coordinator, did, name, type_id),
                    InverterEnergyWeekSensor(coordinator, did, name, type_id),
                    InverterFaultsSensor(coordinator, did, name, type_id),
                    InverterSavingsDaySensor(coordinator, did, name, type_id),
                ]
            )

    async_add_entities(entities)


# ------------------------------------------------------------------
# Geyser sensors
# ------------------------------------------------------------------


class GeyserTempSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting the current water temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_current_temp"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Current temperature"

    @property
    def native_value(self) -> float | None:
        """Return the current temperature in degrees Celsius."""
        return self._details.get("curr_temp")


class GeyserTargetTempSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting the target temperature limit."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_target_temp"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Target temperature"

    @property
    def native_value(self) -> float | None:
        """Return the target temperature in degrees Celsius."""
        return self._details.get("temp_limit")


class GeyserStatusSensor(TeslaConnectEntity, SensorEntity):
    """Sensor showing the device status label from the API."""

    _attr_icon = "mdi:water-boiler"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_status_label"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Status"

    @property
    def native_value(self) -> str | None:
        """Return the human-readable status string."""
        return self._details.get("status_label")


class GeyserModeSensor(TeslaConnectEntity, SensorEntity):
    """Sensor showing the actual operating mode the geyser is currently using.

    In automatic mode the device picks gas or electric based on
    availability, so ``curr_mode`` may differ from ``user_mode``.
    """

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_current_mode"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Current mode"

    @property
    def native_value(self) -> str | None:
        """Return the friendly label for the active mode."""
        mode_val = self._details.get("curr_mode")
        if mode_val is None:
            return None
        return _MODE_LABELS.get(mode_val, str(mode_val))

    @property
    def icon(self) -> str:
        """Return a mode-specific icon."""
        mode_val = self._details.get("curr_mode")
        if mode_val == 0:
            return "mdi:fire"
        if mode_val == 1:
            return "mdi:lightning-bolt"
        if mode_val in (3, 4):
            return "mdi:solar-power"
        return "mdi:auto-fix"


class GeyserUserModeSensor(TeslaConnectEntity, SensorEntity):
    """Sensor showing the mode the user selected (may differ from current)."""

    _attr_icon = "mdi:cog"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_user_mode"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "User mode"

    @property
    def native_value(self) -> str | None:
        """Return the friendly label for the user-selected mode."""
        mode_val = self._details.get("user_mode")
        if mode_val is None:
            return None
        return _MODE_LABELS.get(mode_val, str(mode_val))


class GeyserGasUnitsSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting cumulative gas consumption in cubic metres."""

    _attr_device_class = SensorDeviceClass.GAS
    _attr_icon = "mdi:fire-circle"
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_gas_units"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Gas consumption"

    @property
    def native_value(self) -> int | None:
        """Return the cumulative gas usage in m³."""
        return self._details.get("gas_units")


class GeyserElectricUnitsSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting cumulative electric consumption in kWh.

    The API returns a value in watt-hours; we convert to kWh to match
    the label used in the Android app (which divides by 1000 when the
    value exceeds 1 000 and shows "kW").
    """

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 1

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_electric_units"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Electric consumption"

    @property
    def native_value(self) -> float | None:
        """Return the cumulative electric usage in kWh."""
        raw = self._details.get("electric_units")
        if raw is None:
            return None
        return round(raw / 1000, 1)


class GeyserScheduleSensor(TeslaConnectEntity, SensorEntity):
    """Sensor summarising the active hourly schedule.

    Displays collapsed time ranges such as ``04:00\u201323:00`` and
    exposes individual active hours in extra state attributes.
    """

    _attr_icon = "mdi:calendar-clock"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_schedule"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Schedule"

    @property
    def native_value(self) -> str | None:
        """Return a human-readable summary of active schedule ranges."""
        times: list[dict[str, Any]] = self._details.get("times", [])
        if not times:
            return None

        # Collapse consecutive ON slots into ranges.
        ranges: list[str] = []
        start: int | None = None
        for i, slot in enumerate(times):
            if slot.get("status"):
                if start is None:
                    start = i
            else:
                if start is not None:
                    ranges.append(f"{start:02d}:00\u2013{i:02d}:00")
                    start = None
        if start is not None:
            ranges.append(f"{start:02d}:00\u201300:00")

        if not ranges:
            return "All day OFF"
        if len(ranges) == 1 and ranges[0] == "00:00\u201300:00":
            return "All day ON"
        return ", ".join(ranges)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return per-hour detail attributes."""
        times: list[dict[str, Any]] = self._details.get("times", [])
        active = [i for i, t in enumerate(times) if t.get("status")]
        return {
            "active_count": len(active),
            "active_hours": [f"{h:02d}:00" for h in active],
            "total_slots": len(times),
        }


# ------------------------------------------------------------------
# Inverter sensors
# ------------------------------------------------------------------


class InverterBatteryPercentSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting the inverter battery charge percentage."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_battery_pct"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Battery"

    @property
    def native_value(self) -> int | None:
        """Return the battery percentage."""
        return self._details.get("battery_percentage")


class InverterBatteryVoltageSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting the inverter battery voltage."""

    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_native_unit_of_measurement = "V"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_battery_voltage"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Battery voltage"

    @property
    def native_value(self) -> int | None:
        """Return the battery voltage in volts."""
        return self._details.get("battery_voltage")


class InverterEnergyDaySensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting daily energy production."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_energy_day"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Energy today"

    @property
    def native_value(self) -> int | None:
        """Return today's energy in watt-hours."""
        return self._details.get("energy_day")


class InverterEnergyWeekSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting weekly energy production."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_energy_week"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Energy this week"

    @property
    def native_value(self) -> int | None:
        """Return this week's energy in watt-hours."""
        return self._details.get("energy_week")


class InverterEnergyMonthSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting monthly energy production."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_energy_month"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Energy this month"

    @property
    def native_value(self) -> int | None:
        """Return this month's energy in watt-hours."""
        return self._details.get("energy_month")


class InverterEnergyTotalSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting lifetime energy production."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_energy_total"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Energy total"

    @property
    def native_value(self) -> int | None:
        """Return the lifetime energy in watt-hours."""
        return self._details.get("energy_total")


class InverterSavingsDaySensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting daily energy savings."""

    _attr_icon = "mdi:piggy-bank"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_savings_day"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Savings today"

    @property
    def native_value(self) -> int | None:
        """Return today's savings value."""
        return self._details.get("savings_day")


class InverterFaultsSensor(TeslaConnectEntity, SensorEntity):
    """Sensor reporting the current inverter fault code."""

    _attr_icon = "mdi:alert-circle"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_faults"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Faults"

    @property
    def native_value(self) -> int | None:
        """Return the fault code integer."""
        return self._details.get("faults")

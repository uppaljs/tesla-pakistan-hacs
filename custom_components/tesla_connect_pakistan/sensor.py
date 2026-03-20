"""Sensor platform for Tesla Connect Pakistan."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPE_GEYSER, DEVICE_TYPE_INVERTER, DOMAIN, GEYSER_MODES
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity


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
    _attr_translation_key = "current_temperature"

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
    _attr_translation_key = "target_temperature"

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
    _attr_translation_key = "status_label"

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
    _attr_translation_key = "current_mode"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_current_mode"

    @property
    def name(self) -> str:
        return "Current mode"

    @property
    def native_value(self) -> str | None:
        mode_val = self._details.get("curr_mode")
        return GEYSER_MODES.get(mode_val, str(mode_val)) if mode_val is not None else None

    @property
    def icon(self) -> str:
        return "mdi:fire"


class GeyserUserModeSensor(TeslaConnectEntity, SensorEntity):
    _attr_translation_key = "user_mode"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_user_mode"

    @property
    def name(self) -> str:
        return "User mode"

    @property
    def native_value(self) -> str | None:
        mode_val = self._details.get("user_mode")
        return GEYSER_MODES.get(mode_val, str(mode_val)) if mode_val is not None else None

    @property
    def icon(self) -> str:
        return "mdi:cog"


class GeyserGasUnitsSensor(TeslaConnectEntity, SensorEntity):
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_translation_key = "gas_units"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_gas_units"

    @property
    def name(self) -> str:
        return "Gas units"

    @property
    def native_value(self) -> int | None:
        return self._details.get("gas_units")

    @property
    def icon(self) -> str:
        return "mdi:fire-circle"


class GeyserElectricUnitsSensor(TeslaConnectEntity, SensorEntity):
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_translation_key = "electric_units"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_electric_units"

    @property
    def name(self) -> str:
        return "Electric units"

    @property
    def native_value(self) -> int | None:
        return self._details.get("electric_units")


# ── Inverter sensors ─────────────────────────────────────────────────


class InverterBatteryPercentSensor(TeslaConnectEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "battery_percentage"

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
    _attr_translation_key = "battery_voltage"

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
    _attr_translation_key = "energy_day"

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
    _attr_translation_key = "energy_week"

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
    _attr_translation_key = "energy_month"

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
    _attr_translation_key = "energy_total"

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
    _attr_translation_key = "savings_day"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_savings_day"

    @property
    def name(self) -> str:
        return "Savings today"

    @property
    def native_value(self) -> int | None:
        return self._details.get("savings_day")

    @property
    def icon(self) -> str:
        return "mdi:piggy-bank"


class InverterFaultsSensor(TeslaConnectEntity, SensorEntity):
    _attr_translation_key = "faults"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_faults"

    @property
    def name(self) -> str:
        return "Faults"

    @property
    def native_value(self) -> int | None:
        return self._details.get("faults")

    @property
    def icon(self) -> str:
        return "mdi:alert-circle"

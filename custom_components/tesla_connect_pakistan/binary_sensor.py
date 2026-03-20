"""Binary sensor platform for the Tesla Connect Pakistan integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPE_GEYSER, DEVICE_TYPE_INVERTER
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connect binary sensors from a config entry."""
    coordinator: TeslaConnectCoordinator = entry.runtime_data.coordinator
    entities: list[BinarySensorEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name: str = device.get("name", did)
        type_id: int = data["type_id"]

        # Every device gets a connectivity sensor.
        entities.append(DeviceOnlineSensor(coordinator, did, name, type_id))

        if type_id == DEVICE_TYPE_GEYSER:
            entities.append(GeyserBurnerSensor(coordinator, did, name, type_id))

        if type_id == DEVICE_TYPE_INVERTER:
            entities.append(InverterGridSensor(coordinator, did, name, type_id))
            entities.append(InverterSolarSensor(coordinator, did, name, type_id))

    async_add_entities(entities)


class DeviceOnlineSensor(TeslaConnectEntity, BinarySensorEntity):
    """Binary sensor indicating whether the device is reachable."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_translation_key = "online"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_online"

    @property
    def is_on(self) -> bool | None:
        """Return True when the device is online."""
        return self._device_data.get("device", {}).get("online")


class GeyserBurnerSensor(TeslaConnectEntity, BinarySensorEntity):
    """Binary sensor indicating whether the geyser burner is active."""

    _attr_device_class = BinarySensorDeviceClass.HEAT
    _attr_translation_key = "burner"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_burner"

    @property
    def is_on(self) -> bool | None:
        """Return True when the burner is firing."""
        val = self._details.get("burner")
        return bool(val) if val is not None else None


class InverterGridSensor(TeslaConnectEntity, BinarySensorEntity):
    """Binary sensor indicating whether the grid supply is available."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_translation_key = "grid_status"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_grid_status"

    @property
    def is_on(self) -> bool | None:
        """Return True when grid power is present."""
        val = self._details.get("grid_status")
        return bool(val) if val is not None else None


class InverterSolarSensor(TeslaConnectEntity, BinarySensorEntity):
    """Binary sensor indicating whether the solar input is active."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_translation_key = "solar_status"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_solar_status"

    @property
    def is_on(self) -> bool | None:
        """Return True when solar power is being generated."""
        val = self._details.get("solar_status")
        return bool(val) if val is not None else None

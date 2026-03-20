"""Binary sensor platform for Tesla Connect Pakistan."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPE_GEYSER, DEVICE_TYPE_INVERTER, DOMAIN
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TeslaConnectCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name = device.get("name", did)
        type_id = data["type_id"]

        # Online sensor for every device
        entities.append(DeviceOnlineSensor(coordinator, did, name, type_id))

        if type_id == DEVICE_TYPE_GEYSER:
            entities.append(GeyserBurnerSensor(coordinator, did, name, type_id))

        if type_id == DEVICE_TYPE_INVERTER:
            entities.append(InverterGridSensor(coordinator, did, name, type_id))
            entities.append(InverterSolarSensor(coordinator, did, name, type_id))

    async_add_entities(entities)


class DeviceOnlineSensor(TeslaConnectEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_online"

    @property
    def name(self) -> str:
        return "Online"

    @property
    def is_on(self) -> bool | None:
        dev = self._device_data.get("device", {})
        return dev.get("online")


class GeyserBurnerSensor(TeslaConnectEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.HEAT

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_burner"

    @property
    def name(self) -> str:
        return "Burner"

    @property
    def is_on(self) -> bool | None:
        val = self._details.get("burner")
        return bool(val) if val is not None else None


class InverterGridSensor(TeslaConnectEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.POWER

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_grid_status"

    @property
    def name(self) -> str:
        return "Grid"

    @property
    def is_on(self) -> bool | None:
        val = self._details.get("grid_status")
        return bool(val) if val is not None else None


class InverterSolarSensor(TeslaConnectEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.POWER

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_solar_status"

    @property
    def name(self) -> str:
        return "Solar"

    @property
    def is_on(self) -> bool | None:
        val = self._details.get("solar_status")
        return bool(val) if val is not None else None

    @property
    def icon(self) -> str:
        return "mdi:solar-power"

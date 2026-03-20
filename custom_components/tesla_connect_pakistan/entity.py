"""Base entity for Tesla Connect Pakistan."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPE_GEYSER, DEVICE_TYPE_INVERTER, DOMAIN, MANUFACTURER
from .coordinator import TeslaConnectCoordinator


class TeslaConnectEntity(CoordinatorEntity[TeslaConnectCoordinator]):
    """Base class for all Tesla Connect entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TeslaConnectCoordinator,
        device_id: str,
        device_name: str,
        device_type: int,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._device_type = device_type

    @property
    def device_info(self) -> DeviceInfo:
        model = "Geyser" if self._device_type == DEVICE_TYPE_GEYSER else "Inverter"
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=self._device_name,
            manufacturer=MANUFACTURER,
            model=model,
        )

    @property
    def _device_data(self) -> dict:
        """Shortcut to this device's coordinator data."""
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id]
        return {}

    @property
    def _details(self) -> dict:
        return self._device_data.get("details", {})

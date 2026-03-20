"""Base entity for the Tesla Connect Pakistan integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPE_GEYSER, DOMAIN, MANUFACTURER
from .coordinator import TeslaConnectCoordinator


class TeslaConnectEntity(CoordinatorEntity[TeslaConnectCoordinator]):
    """Base class shared by all Tesla Connect entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TeslaConnectCoordinator,
        device_id: str,
        device_name: str,
        device_type: int,
    ) -> None:
        """Initialise the base entity.

        Args:
            coordinator: The shared data-update coordinator.
            device_id: Unique device identifier from the API.
            device_name: Human-readable device name.
            device_type: Device type constant (DEVICE_TYPE_GEYSER, etc.).

        """
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._device_type = device_type

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        model = "Geyser" if self._device_type == DEVICE_TYPE_GEYSER else "Inverter"
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer=MANUFACTURER,
            model=model,
            name=self._device_name,
        )

    @property
    def _device_data(self) -> dict[str, Any]:
        """Return this device's section of the coordinator data."""
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id]
        return {}

    @property
    def _details(self) -> dict[str, Any]:
        """Return the detail payload for this device."""
        return self._device_data.get("details", {})

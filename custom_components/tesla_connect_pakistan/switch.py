"""Switch platform for Tesla Connect Pakistan."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICE_TYPE_GEYSER, DOMAIN
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TeslaConnectCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SwitchEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name = device.get("name", did)
        type_id = data["type_id"]

        if type_id == DEVICE_TYPE_GEYSER:
            entities.extend(
                [
                    GeyserBoostSwitch(coordinator, did, name, type_id),
                    GeyserVacationSwitch(coordinator, did, name, type_id),
                    GeyserTwoHourSwitch(coordinator, did, name, type_id),
                ]
            )
            # One switch per hourly time slot (24 switches)
            for hour in range(24):
                entities.append(
                    GeyserTimerSlotSwitch(coordinator, did, name, type_id, hour)
                )

    async_add_entities(entities)


class GeyserBoostSwitch(TeslaConnectEntity, SwitchEntity):
    _attr_icon = "mdi:flash"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_boost"

    @property
    def name(self) -> str:
        return "Boost"

    @property
    def is_on(self) -> bool | None:
        val = self._details.get("boost")
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost, self._device_id, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost, self._device_id, False
        )
        await self.coordinator.async_request_refresh()


class GeyserVacationSwitch(TeslaConnectEntity, SwitchEntity):
    _attr_icon = "mdi:beach"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_vacation"

    @property
    def name(self) -> str:
        return "Vacation mode"

    @property
    def is_on(self) -> bool | None:
        val = self._details.get("vacation")
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode, self._device_id, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode, self._device_id, False
        )
        await self.coordinator.async_request_refresh()


class GeyserTwoHourSwitch(TeslaConnectEntity, SwitchEntity):
    _attr_icon = "mdi:timer-2"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_two_hour"

    @property
    def name(self) -> str:
        return "Two-hour mode"

    @property
    def is_on(self) -> bool | None:
        val = self._details.get("two_hour_mode")
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_two_hour_mode, self._device_id, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_two_hour_mode, self._device_id, False
        )
        await self.coordinator.async_request_refresh()


class GeyserTimerSlotSwitch(TeslaConnectEntity, SwitchEntity):
    """Switch for an individual hourly timer slot (0–23).

    Toggling a slot sends the full 24-slot schedule to the API,
    with only the target slot changed.
    """

    _attr_icon = "mdi:clock-outline"

    def __init__(
        self,
        coordinator: TeslaConnectCoordinator,
        device_id: str,
        device_name: str,
        device_type: int,
        hour: int,
    ) -> None:
        super().__init__(coordinator, device_id, device_name, device_type)
        self._hour = hour

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_timer_{self._hour:02d}"

    @property
    def name(self) -> str:
        return f"Timer {self._hour:02d}:00"

    @property
    def _current_times(self) -> list[dict]:
        """Return the current 24-slot schedule from coordinator data."""
        return self._details.get("times", [])

    @property
    def is_on(self) -> bool | None:
        times = self._current_times
        if self._hour < len(times):
            return times[self._hour].get("status")
        return None

    def _build_updated_times(self, target_status: bool) -> list[dict]:
        """Clone the current schedule with one slot changed."""
        times = self._current_times
        updated = []
        for i, slot in enumerate(times):
            updated.append({
                "time": slot["time"],
                "status": target_status if i == self._hour else slot["status"],
            })
        return updated

    async def async_turn_on(self, **kwargs: Any) -> None:
        new_times = self._build_updated_times(True)
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_timer, self._device_id, new_times
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        new_times = self._build_updated_times(False)
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_timer, self._device_id, new_times
        )
        await self.coordinator.async_request_refresh()

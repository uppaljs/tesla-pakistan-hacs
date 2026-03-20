"""Switch platform for the Tesla Connect Pakistan integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ENABLE_SCHEDULE_SWITCHES, DEVICE_TYPE_GEYSER, DOMAIN
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connect switches from a config entry."""
    coordinator: TeslaConnectCoordinator = hass.data[DOMAIN][entry.entry_id]
    enable_schedule: bool = entry.options.get(CONF_ENABLE_SCHEDULE_SWITCHES, True)
    entities: list[SwitchEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name: str = device.get("name", did)
        type_id: int = data["type_id"]

        if type_id == DEVICE_TYPE_GEYSER:
            entities.extend(
                [
                    GeyserBoostSwitch(coordinator, did, name, type_id),
                    GeyserTwoHourSwitch(coordinator, did, name, type_id),
                    GeyserVacationSwitch(coordinator, did, name, type_id),
                ]
            )
            # Only create the 24 hourly schedule switches when enabled.
            if enable_schedule:
                for hour in range(24):
                    entities.append(GeyserTimerSlotSwitch(coordinator, did, name, type_id, hour))

    async_add_entities(entities)


# ------------------------------------------------------------------
# Feature switches
# ------------------------------------------------------------------


class GeyserBoostSwitch(TeslaConnectEntity, SwitchEntity):
    """Switch to activate instant-heat boost mode on a geyser."""

    _attr_icon = "mdi:flash"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_boost"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Boost"

    @property
    def is_on(self) -> bool | None:
        """Return True when boost mode is active."""
        val = self._details.get("boost")
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable boost mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost, self._device_id, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable boost mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost, self._device_id, False
        )
        await self.coordinator.async_request_refresh()


class GeyserTwoHourSwitch(TeslaConnectEntity, SwitchEntity):
    """Switch to activate the two-hour heating window."""

    _attr_icon = "mdi:timer-2"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_two_hour"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Two-hour mode"

    @property
    def is_on(self) -> bool | None:
        """Return True when two-hour mode is active."""
        val = self._details.get("two_hour_mode")
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable two-hour mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_two_hour_mode, self._device_id, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable two-hour mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_two_hour_mode, self._device_id, False
        )
        await self.coordinator.async_request_refresh()


class GeyserVacationSwitch(TeslaConnectEntity, SwitchEntity):
    """Switch to activate vacation mode (away) on a geyser."""

    _attr_icon = "mdi:beach"

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_vacation"

    @property
    def name(self) -> str:
        """Return the display name."""
        return "Vacation mode"

    @property
    def is_on(self) -> bool | None:
        """Return True when vacation mode is active."""
        val = self._details.get("vacation")
        return bool(val) if val is not None else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable vacation mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode, self._device_id, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable vacation mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode, self._device_id, False
        )
        await self.coordinator.async_request_refresh()


# ------------------------------------------------------------------
# Hourly schedule switches
# ------------------------------------------------------------------


class GeyserTimerSlotSwitch(TeslaConnectEntity, SwitchEntity):
    """Switch controlling a single hourly slot in the geyser schedule.

    Toggling a slot sends the complete 24-slot schedule to the API
    with only the target slot changed.  These entities are placed in
    the CONFIG category so they appear under device configuration
    rather than on the main dashboard.
    """

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: TeslaConnectCoordinator,
        device_id: str,
        device_name: str,
        device_type: int,
        hour: int,
    ) -> None:
        """Initialise a timer-slot switch.

        Args:
            coordinator: The shared data-update coordinator.
            device_id: Unique device identifier from the API.
            device_name: Human-readable device name.
            device_type: Device type constant.
            hour: Hour of the day (0–23) this switch controls.

        """
        super().__init__(coordinator, device_id, device_name, device_type)
        self._hour = hour

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_timer_{self._hour:02d}"

    @property
    def name(self) -> str:
        """Return the display name."""
        end = (self._hour + 1) % 24
        return f"Schedule {self._hour:02d}:00\u2013{end:02d}:00"

    @property
    def icon(self) -> str:
        """Return a dynamic icon based on slot state."""
        if self.is_on:
            return "mdi:clock-check"
        return "mdi:clock-outline"

    @property
    def _current_times(self) -> list[dict[str, Any]]:
        """Return the current 24-slot schedule from coordinator data."""
        return self._details.get("times", [])

    @property
    def is_on(self) -> bool | None:
        """Return True when this hourly slot is enabled."""
        times = self._current_times
        if self._hour < len(times):
            return times[self._hour].get("status")
        return None

    def _build_updated_times(self, target_status: bool) -> list[dict[str, Any]]:
        """Clone the current schedule with a single slot changed.

        Args:
            target_status: The desired on/off state for this slot.

        Returns:
            A full 24-slot list suitable for the set_geyser_timer API.

        """
        return [
            {
                "status": target_status if i == self._hour else slot["status"],
                "time": slot["time"],
            }
            for i, slot in enumerate(self._current_times)
        ]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable this schedule slot."""
        new_times = self._build_updated_times(True)
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_timer, self._device_id, new_times
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable this schedule slot."""
        new_times = self._build_updated_times(False)
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_timer, self._device_id, new_times
        )
        await self.coordinator.async_request_refresh()

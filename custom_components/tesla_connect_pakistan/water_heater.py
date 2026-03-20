"""Water heater platform for the Tesla Connect Pakistan integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_GAS,
    STATE_OFF,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEVICE_TYPE_GEYSER,
    GEYSER_MODE_AUTOMATIC,
    GEYSER_MODE_ELECTRICITY,
    GEYSER_MODE_GAS,
    GEYSER_MODE_SOLAR_DISABLED,
    GEYSER_MODE_SOLAR_ENABLED,
    GEYSER_MODES,
    GEYSER_MODES_REVERSE,
)
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

# Operation modes exposed in the HA UI.
OPERATION_LIST = sorted(GEYSER_MODES_REVERSE.keys())

# Map the Tesla geyser curr_mode integer to an HA state constant.
_MODE_TO_HA_STATE: dict[int, str] = {
    GEYSER_MODE_AUTOMATIC: STATE_ECO,
    GEYSER_MODE_ELECTRICITY: STATE_ELECTRIC,
    GEYSER_MODE_GAS: STATE_GAS,
    GEYSER_MODE_SOLAR_DISABLED: STATE_ELECTRIC,
    GEYSER_MODE_SOLAR_ENABLED: STATE_ECO,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connect water heater entities from a config entry."""
    coordinator: TeslaConnectCoordinator = entry.runtime_data.coordinator
    entities: list[WaterHeaterEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name: str = device.get("name", did)
        type_id: int = data["type_id"]

        if type_id == DEVICE_TYPE_GEYSER:
            entities.append(TeslaGeyserWaterHeater(coordinator, did, name, type_id))

    async_add_entities(entities)


class TeslaGeyserWaterHeater(TeslaConnectEntity, WaterHeaterEntity):
    """Water heater entity representing a Tesla Connect geyser.

    Supported HA features:

    * **TARGET_TEMPERATURE** — set temperature (30-75 C).
    * **OPERATION_MODE** — gas / electric / auto / solar_on / solar_off.
    * **AWAY_MODE** — maps to vacation mode.
    * **ON_OFF** — turn_on activates boost; turn_off deactivates it.
    """

    _attr_translation_key = "water_heater"
    _attr_max_temp = 75
    _attr_min_temp = 30
    _attr_operation_list = OPERATION_LIST
    _attr_supported_features = (
        WaterHeaterEntityFeature.AWAY_MODE
        | WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.TARGET_TEMPERATURE
    )
    _attr_target_temperature_step = 1.0
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def unique_id(self) -> str:
        """Return a unique identifier for this entity."""
        return f"{self._device_id}_water_heater"

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def state(self) -> str | None:
        """Return the HA state constant based on the current operating mode.

        ``curr_mode`` reflects what the geyser is *actually* running on
        (e.g. gas), while ``user_mode`` is the preference the user set
        (e.g. automatic).  In automatic mode the device picks gas or
        electric based on availability, so the two may differ.  We
        report what the geyser is actually doing.
        """
        if self._details.get("vacation"):
            return STATE_OFF
        mode_val = self._details.get("curr_mode")
        if mode_val is None:
            return None
        return _MODE_TO_HA_STATE.get(mode_val, STATE_GAS)

    # ------------------------------------------------------------------
    # Temperatures
    # ------------------------------------------------------------------

    @property
    def current_temperature(self) -> float | None:
        """Return the current water temperature."""
        return self._details.get("curr_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature limit."""
        return self._details.get("temp_limit")

    # ------------------------------------------------------------------
    # Operation mode
    # ------------------------------------------------------------------

    @property
    def current_operation(self) -> str | None:
        """Return the user-selected operation mode as a string."""
        mode_val = self._details.get("user_mode")
        return GEYSER_MODES.get(mode_val)

    # ------------------------------------------------------------------
    # Away mode (vacation)
    # ------------------------------------------------------------------

    @property
    def is_away_mode_on(self) -> bool | None:
        """Return True when vacation mode is active."""
        val = self._details.get("vacation")
        return bool(val) if val is not None else None

    # ------------------------------------------------------------------
    # Extra attributes
    # ------------------------------------------------------------------

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return supplementary attributes not covered by standard properties."""
        return {
            "boost": bool(self._details.get("boost")),
            "burner": bool(self._details.get("burner")),
            "electric_units": self._details.get("electric_units"),
            "gas_units": self._details.get("gas_units"),
            "solar": bool(self._details.get("solar")),
            "status_label": self._details.get("status_label"),
            "temp_label": self._details.get("temp_label"),
            "two_hour_mode": bool(self._details.get("two_hour_mode")),
            "vacation": bool(self._details.get("vacation")),
        }

    # ------------------------------------------------------------------
    # Actions: temperature
    # ------------------------------------------------------------------

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temp = kwargs.get("temperature")
        if temp is None:
            return
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_temp_limit,
            self._device_id,
            int(temp),
        )
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Actions: operation mode
    # ------------------------------------------------------------------

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set the geyser operating mode."""
        mode_int = GEYSER_MODES_REVERSE.get(operation_mode)
        if mode_int is None:
            _LOGGER.error("Unknown operation mode: %s", operation_mode)
            return
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_mode,
            self._device_id,
            mode_int,
            mode_int,
        )
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Actions: away mode (vacation)
    # ------------------------------------------------------------------

    async def async_turn_away_mode_on(self, **kwargs: Any) -> None:
        """Activate vacation mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode,
            self._device_id,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_off(self, **kwargs: Any) -> None:
        """Deactivate vacation mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode,
            self._device_id,
            False,
        )
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Actions: on / off (boost)
    # ------------------------------------------------------------------

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the geyser by activating boost mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost,
            self._device_id,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the geyser by deactivating boost mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost,
            self._device_id,
            False,
        )
        await self.coordinator.async_request_refresh()

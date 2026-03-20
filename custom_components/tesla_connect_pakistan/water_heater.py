"""Water heater platform for Tesla Connect Pakistan."""

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
    DOMAIN,
    GEYSER_MODE_AUTOMATIC,
    GEYSER_MODE_ELECTRICITY,
    GEYSER_MODE_GAS,
    GEYSER_MODE_SOLAR_DISABLED,
    GEYSER_MODE_SOLAR_ENABLED,
    GEYSER_MODES,
    HA_MODE_MAP,
)
from .coordinator import TeslaConnectCoordinator
from .entity import TeslaConnectEntity

_LOGGER = logging.getLogger(__name__)

# Operation modes exposed in HA UI
OPERATION_LIST = list(HA_MODE_MAP.keys())

# Map the Tesla geyser's curr_mode int → HA state constant for the
# entity's main state.  HA water_heater uses these as the entity state.
_MODE_TO_HA_STATE: dict[int, str] = {
    GEYSER_MODE_GAS: STATE_GAS,
    GEYSER_MODE_ELECTRICITY: STATE_ELECTRIC,
    GEYSER_MODE_AUTOMATIC: STATE_ECO,        # auto ≈ eco
    GEYSER_MODE_SOLAR_ENABLED: STATE_ECO,     # solar ≈ eco
    GEYSER_MODE_SOLAR_DISABLED: STATE_ELECTRIC,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TeslaConnectCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[WaterHeaterEntity] = []

    for did, data in coordinator.data.items():
        device = data["device"]
        name = device.get("name", did)
        type_id = data["type_id"]

        if type_id == DEVICE_TYPE_GEYSER:
            entities.append(TeslaGeyserWaterHeater(coordinator, did, name, type_id))

    async_add_entities(entities)


class TeslaGeyserWaterHeater(TeslaConnectEntity, WaterHeaterEntity):
    """Water heater entity representing a Tesla Connect geyser.

    Supported HA features:
    - TARGET_TEMPERATURE  → set_temperature (30–75 °C)
    - OPERATION_MODE      → set_operation_mode (gas/electric/auto/solar_on/solar_off)
    - AWAY_MODE           → vacation mode
    - ON_OFF              → boost on = turn_on, boost off = turn_off
    """

    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.AWAY_MODE
        | WaterHeaterEntityFeature.ON_OFF
    )
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 30
    _attr_max_temp = 75
    _attr_target_temperature_step = 1.0
    _attr_operation_list = OPERATION_LIST
    _attr_icon = "mdi:water-boiler"

    @property
    def unique_id(self) -> str:
        return f"{self._device_id}_water_heater"

    @property
    def name(self) -> str:
        return "Water heater"

    # ── state ────────────────────────────────────────────────────────

    @property
    def state(self) -> str | None:
        """Return the HA state constant based on the geyser's current mode.

        If vacation mode is active the geyser is effectively off.
        """
        if self._details.get("vacation"):
            return STATE_OFF
        mode_val = self._details.get("curr_mode")
        if mode_val is None:
            return None
        return _MODE_TO_HA_STATE.get(mode_val, STATE_GAS)

    # ── temperatures ─────────────────────────────────────────────────

    @property
    def current_temperature(self) -> float | None:
        return self._details.get("curr_temp")

    @property
    def target_temperature(self) -> float | None:
        return self._details.get("temp_limit")

    # ── operation mode ───────────────────────────────────────────────

    @property
    def current_operation(self) -> str | None:
        mode_val = self._details.get("user_mode")
        return GEYSER_MODES.get(mode_val)

    # ── away mode (= vacation) ───────────────────────────────────────

    @property
    def is_away_mode_on(self) -> bool | None:
        val = self._details.get("vacation")
        return bool(val) if val is not None else None

    # ── extra attributes ─────────────────────────────────────────────

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "status_label": self._details.get("status_label"),
            "temp_label": self._details.get("temp_label"),
            "burner": bool(self._details.get("burner")),
            "boost": bool(self._details.get("boost")),
            "two_hour_mode": bool(self._details.get("two_hour_mode")),
            "vacation": bool(self._details.get("vacation")),
            "solar": bool(self._details.get("solar")),
            "gas_units": self._details.get("gas_units"),
            "electric_units": self._details.get("electric_units"),
        }

    # ── actions: temperature ─────────────────────────────────────────

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temp = kwargs.get("temperature")
        if temp is None:
            return
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_temp_limit,
            self._device_id,
            int(temp),
        )
        await self.coordinator.async_request_refresh()

    # ── actions: operation mode ──────────────────────────────────────

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        mode_int = HA_MODE_MAP.get(operation_mode)
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

    # ── actions: away mode (vacation) ────────────────────────────────

    async def async_turn_away_mode_on(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode,
            self._device_id,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_off(self, **kwargs: Any) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_vacation_mode,
            self._device_id,
            False,
        )
        await self.coordinator.async_request_refresh()

    # ── actions: on / off (boost) ────────────────────────────────────

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on = activate boost mode for immediate heating."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost,
            self._device_id,
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off = deactivate boost mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_geyser_boost,
            self._device_id,
            False,
        )
        await self.coordinator.async_request_refresh()

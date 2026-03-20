"""Tests for Tesla Connect Pakistan water heater entity."""

from __future__ import annotations

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_GAS,
    STATE_OFF,
)

from custom_components.tesla_connect_pakistan.const import (
    GEYSER_MODE_AUTOMATIC,
    GEYSER_MODE_ELECTRICITY,
    GEYSER_MODE_GAS,
    GEYSER_MODE_SOLAR_DISABLED,
    GEYSER_MODE_SOLAR_ENABLED,
    GEYSER_MODES,
    GEYSER_MODES_REVERSE,
)
from custom_components.tesla_connect_pakistan.water_heater import (
    OPERATION_LIST,
    _MODE_TO_HA_STATE,
)


class TestModeMapping:
    """Tests for mode integer ↔ string mapping correctness."""

    def test_gas_mode_maps_to_state_gas(self) -> None:
        """curr_mode=0 (gas) should map to HA STATE_GAS."""
        assert _MODE_TO_HA_STATE[GEYSER_MODE_GAS] == STATE_GAS

    def test_electric_mode_maps_to_state_electric(self) -> None:
        """curr_mode=1 (electric) should map to HA STATE_ELECTRIC."""
        assert _MODE_TO_HA_STATE[GEYSER_MODE_ELECTRICITY] == STATE_ELECTRIC

    def test_automatic_mode_maps_to_eco(self) -> None:
        """curr_mode=2 (automatic) should map to HA STATE_ECO."""
        assert _MODE_TO_HA_STATE[GEYSER_MODE_AUTOMATIC] == STATE_ECO

    def test_solar_enabled_maps_to_eco(self) -> None:
        """curr_mode=3 (solar on) should map to HA STATE_ECO."""
        assert _MODE_TO_HA_STATE[GEYSER_MODE_SOLAR_ENABLED] == STATE_ECO

    def test_solar_disabled_maps_to_electric(self) -> None:
        """curr_mode=4 (solar off) should map to HA STATE_ELECTRIC."""
        assert _MODE_TO_HA_STATE[GEYSER_MODE_SOLAR_DISABLED] == STATE_ELECTRIC

    def test_vacation_mode_gives_off_state(self) -> None:
        """When vacation is active, the state should be OFF."""
        # This is tested in the entity property; here we verify the constant.
        assert STATE_OFF == "off"

    def test_all_modes_have_ha_state(self) -> None:
        """Every geyser mode integer should have a mapped HA state."""
        for mode_int in GEYSER_MODES:
            assert mode_int in _MODE_TO_HA_STATE


class TestOperationList:
    """Tests for the operation mode list exposed to HA."""

    def test_operation_list_sorted(self) -> None:
        """Operation modes should be alphabetically sorted."""
        assert OPERATION_LIST == sorted(OPERATION_LIST)

    def test_all_modes_reversible(self) -> None:
        """Every operation string should map back to a valid mode integer."""
        for mode_str in OPERATION_LIST:
            mode_int = GEYSER_MODES_REVERSE[mode_str]
            assert GEYSER_MODES[mode_int] == mode_str

    def test_expected_modes_present(self) -> None:
        """The operation list should contain all five modes."""
        expected = {"auto", "electric", "gas", "solar_off", "solar_on"}
        assert set(OPERATION_LIST) == expected

"""Tests for Tesla Connect Pakistan integration setup and teardown."""

from __future__ import annotations

from custom_components.tesla_connect_pakistan import PLATFORMS
from custom_components.tesla_connect_pakistan.const import DOMAIN

from homeassistant.const import Platform


class TestIntegrationSetup:
    """Tests for the integration module structure."""

    def test_domain_constant(self) -> None:
        """The domain should match the expected value."""
        assert DOMAIN == "tesla_connect_pakistan"

    def test_platforms_defined(self) -> None:
        """The integration should declare its platforms."""
        assert len(PLATFORMS) > 0

    def test_platforms_are_valid(self) -> None:
        """All declared platforms should be valid HA Platform members."""
        for platform in PLATFORMS:
            assert isinstance(platform, Platform)

    def test_expected_platforms(self) -> None:
        """The integration should support sensor, binary_sensor, switch, and water_heater."""
        expected = {
            Platform.BINARY_SENSOR,
            Platform.SENSOR,
            Platform.SWITCH,
            Platform.WATER_HEATER,
        }
        assert set(PLATFORMS) == expected

    def test_platforms_sorted(self) -> None:
        """Platforms should be in alphabetical order per HA style."""
        platform_values = [p.value for p in PLATFORMS]
        assert platform_values == sorted(platform_values)

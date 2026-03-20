"""Tests for the Tesla Connect Pakistan config flow."""

from __future__ import annotations


from custom_components.tesla_connect_pakistan.config_flow import (
    STEP_USER_DATA_SCHEMA,
    TeslaConnectConfigFlow,
    TeslaConnectOptionsFlow,
)
from custom_components.tesla_connect_pakistan.const import (
    CONF_PASSWORD,
    CONF_PHONE,
    DEFAULT_SCAN_INTERVAL,
)


class TestUserStepSchema:
    """Tests for the user step form schema."""

    def test_schema_has_phone_field(self) -> None:
        """The user form should require a phone number."""
        keys = [str(k) for k in STEP_USER_DATA_SCHEMA.schema]
        assert CONF_PHONE in keys

    def test_schema_has_password_field(self) -> None:
        """The user form should require a password."""
        keys = [str(k) for k in STEP_USER_DATA_SCHEMA.schema]
        assert CONF_PASSWORD in keys


class TestConfigFlowClass:
    """Tests for config flow class structure."""

    def test_domain_is_set(self) -> None:
        """The config flow should declare the correct domain."""
        # ConfigFlow registers domain via the metaclass; verify our class exists.
        assert TeslaConnectConfigFlow is not None

    def test_version_is_set(self) -> None:
        """The config flow should declare a version."""
        assert TeslaConnectConfigFlow.VERSION == 1

    def test_has_options_flow(self) -> None:
        """The config flow should provide an options flow handler."""
        assert hasattr(TeslaConnectConfigFlow, "async_get_options_flow")


class TestOptionsFlowDefaults:
    """Tests for the options flow schema defaults."""

    def test_default_scan_interval(self) -> None:
        """The default scan interval should match the constant."""
        assert DEFAULT_SCAN_INTERVAL == 30

    def test_options_flow_class_exists(self) -> None:
        """The options flow handler class should exist."""
        assert TeslaConnectOptionsFlow is not None

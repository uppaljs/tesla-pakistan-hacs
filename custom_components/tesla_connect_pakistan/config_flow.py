"""Config flow for the Tesla Connect Pakistan integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .api import TeslaConnectApi, TeslaConnectApiError, TeslaConnectAuthError
from .const import CONF_PASSWORD, CONF_PHONE, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class TeslaConnectConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesla Connect Pakistan."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            phone = user_input[CONF_PHONE]
            password = user_input[CONF_PASSWORD]

            api = TeslaConnectApi(phone, password)
            try:
                await self.hass.async_add_executor_job(api.sign_in)
            except TeslaConnectAuthError:
                errors["base"] = "invalid_auth"
            except TeslaConnectApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during login")
                errors["base"] = "unknown"
            else:
                # Prevent duplicate entries for the same phone number.
                await self.async_set_unique_id(phone)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Tesla Connect ({api.user_name or phone})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

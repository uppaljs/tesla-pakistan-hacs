"""Config flow for the Tesla Connect Pakistan integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback

from .api import TeslaConnectApi, TeslaConnectApiError, TeslaConnectAuthError
from .const import (
    CONF_ENABLE_SCHEDULE_SWITCHES,
    CONF_PASSWORD,
    CONF_PHONE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> TeslaConnectOptionsFlow:
        """Create the options flow handler."""
        return TeslaConnectOptionsFlow()

    # ------------------------------------------------------------------
    # User step (initial setup)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Reauth flow (triggered by ConfigEntryAuthFailed)
    # ------------------------------------------------------------------

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication when credentials expire."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Prompt the user to re-enter credentials."""
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
                _LOGGER.exception("Unexpected error during reauth")
                errors["base"] = "unknown"
            else:
                reauth_entry = self._get_reauth_entry()
                await self.async_set_unique_id(phone)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Reconfigure flow (update phone/password on existing entry)
    # ------------------------------------------------------------------

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
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
                _LOGGER.exception("Unexpected error during reconfigure")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(phone)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates=user_input,
                )

        reconfigure_entry = self._get_reconfigure_entry()
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PHONE,
                        default=reconfigure_entry.data.get(CONF_PHONE, ""),
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


# ------------------------------------------------------------------
# Options flow
# ------------------------------------------------------------------

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=10, max=300)
        ),
        vol.Required(CONF_ENABLE_SCHEDULE_SWITCHES, default=True): bool,
    }
)


class TeslaConnectOptionsFlow(OptionsFlowWithReload):
    """Handle options for Tesla Connect Pakistan.

    Uses OptionsFlowWithReload so that the integration automatically
    reloads when the user saves new options, picking up the updated
    scan interval and entity configuration without a manual restart.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )

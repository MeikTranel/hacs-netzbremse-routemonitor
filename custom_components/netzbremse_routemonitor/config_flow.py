"""Config flow for Netzbremse Routemonitor integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .const import CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL, DOMAIN, MAX_POLLING_INTERVAL, MIN_POLLING_INTERVAL

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


class NetzbremseRoutemonitorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Netzbremse Routemonitor."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step.

        Args:
            user_input: User-provided configuration data.

        Returns:
            Config flow result (form or create entry).
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate polling interval
            polling_interval = user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

            if not MIN_POLLING_INTERVAL <= polling_interval <= MAX_POLLING_INTERVAL:
                errors[CONF_POLLING_INTERVAL] = "invalid_interval"
            else:
                # Create the config entry
                return self.async_create_entry(
                    title="Netzbremse Routemonitor",
                    data=user_input,
                )

        # Show the configuration form
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POLLING_INTERVAL,
                    default=DEFAULT_POLLING_INTERVAL,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_POLLING_INTERVAL, max=MAX_POLLING_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> NetzbremseRoutemonitorOptionsFlow:
        """Get the options flow for this handler.

        Args:
            config_entry: The config entry to create options flow for.

        Returns:
            Options flow instance.
        """
        return NetzbremseRoutemonitorOptionsFlow()


class NetzbremseRoutemonitorOptionsFlow(OptionsFlow):
    """Handle options flow for Netzbremse Routemonitor."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options.

        Args:
            user_input: User-provided options data.

        Returns:
            Config flow result (form or create entry).
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate polling interval
            polling_interval = user_input.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

            if not MIN_POLLING_INTERVAL <= polling_interval <= MAX_POLLING_INTERVAL:
                errors[CONF_POLLING_INTERVAL] = "invalid_interval"
            else:
                # Update the config entry with new options
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=user_input,
                )
                return self.async_create_entry(title="", data={})

        # Get current polling interval from config entry
        current_interval = self.config_entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

        # Show the options form
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_POLLING_INTERVAL,
                    default=current_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_POLLING_INTERVAL, max=MAX_POLLING_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )

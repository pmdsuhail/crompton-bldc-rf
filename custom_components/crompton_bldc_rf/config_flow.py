"""Config flow for the Crompton BLDC RF Remote integration."""

from __future__ import annotations

from typing import Any

from rf_protocols import ModulationType
import voluptuous as vol

from homeassistant.components.radio_frequency import (
    DOMAIN as RADIO_FREQUENCY_DOMAIN,
    async_get_transmitters,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er, selector
from homeassistant.util import slugify

from .codes import DEFAULT_MODEL, MODELS
from .const import CONF_MODEL, CONF_TRANSMITTER, DEFAULT_NAME, DOMAIN, FREQUENCY_HZ


class CromptonBldcRfConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for a Crompton BLDC fan."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick a name, the transmitter and (when there are several) the model."""
        try:
            transmitters = async_get_transmitters(
                self.hass, FREQUENCY_HZ, ModulationType.OOK
            )
        except HomeAssistantError:
            return self.async_abort(reason="no_transmitters")
        if not transmitters:
            return self.async_abort(
                reason="no_compatible_transmitters",
                description_placeholders={"frequency": "433.92 MHz", "modulation": "OOK"},
            )

        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip() or DEFAULT_NAME
            entity_entry = er.async_get(self.hass).async_get(
                user_input[CONF_TRANSMITTER]
            )
            if entity_entry is None:
                errors[CONF_TRANSMITTER] = "transmitter_not_found"
            else:
                await self.async_set_unique_id(f"{entity_entry.id}_{slugify(name)}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_TRANSMITTER: entity_entry.entity_id,
                        CONF_MODEL: user_input.get(CONF_MODEL, DEFAULT_MODEL),
                    },
                )

        fields: dict[vol.Marker, Any] = {
            vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(),
            vol.Required(CONF_TRANSMITTER): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=RADIO_FREQUENCY_DOMAIN, include_entities=transmitters
                )
            ),
        }
        if len(MODELS) > 1:
            fields[vol.Required(CONF_MODEL, default=DEFAULT_MODEL)] = (
                selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(MODELS),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        translation_key=CONF_MODEL,
                    )
                )
            )
        schema = vol.Schema(fields)
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

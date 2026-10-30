"""The Crompton BLDC RF Remote integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .codes import MODELS
from .const import CONF_MODEL, CONF_TRANSMITTER, DOMAIN
from .remote import CromptonConfigEntry, CromptonRemote

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.FAN]


async def async_setup_entry(hass: HomeAssistant, entry: CromptonConfigEntry) -> bool:
    """Set up a Crompton fan from a config entry."""
    model = MODELS.get(entry.data[CONF_MODEL])
    if model is None:
        raise ConfigEntryError(
            translation_domain=DOMAIN,
            translation_key="unknown_model",
            translation_placeholders={"model": entry.data[CONF_MODEL]},
        )
    entry.runtime_data = CromptonRemote(hass, entry.data[CONF_TRANSMITTER], model)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CromptonConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

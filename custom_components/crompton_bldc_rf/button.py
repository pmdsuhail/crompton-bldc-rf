"""Buttons for the keys of a Crompton BLDC fan remote."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import BUTTON_KEYS, CromptonKey
from .entity import CromptonEntity
from .remote import CromptonConfigEntry

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CromptonConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add one button per remote key that has a code."""
    remote = entry.runtime_data
    async_add_entities(
        CromptonButton(entry, key) for key in BUTTON_KEYS if remote.supports(key)
    )


class CromptonButton(CromptonEntity, ButtonEntity):
    """A key on the Crompton remote."""

    def __init__(self, entry: CromptonConfigEntry, key: CromptonKey) -> None:
        """Initialize the button."""
        super().__init__(entry)
        self._key = key
        self._attr_translation_key = key.value
        self._attr_unique_id = f"{entry.entry_id}_{key.value}"

    async def async_press(self) -> None:
        """Send the key."""
        await self._remote.async_send(self._key, context=self._context)

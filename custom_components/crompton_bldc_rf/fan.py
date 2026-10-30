"""Fan entity for a Crompton BLDC fan controlled by RF."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import (
    ATTR_PERCENTAGE,
    ATTR_PRESET_MODE,
    FanEntity,
    FanEntityFeature,
)
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .codes import SPEED_KEYS, CromptonKey
from .const import PRESET_HYPER
from .entity import CromptonEntity
from .remote import CromptonConfigEntry

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CromptonConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the fan entity."""
    async_add_entities([CromptonFan(entry)])


class CromptonFan(CromptonEntity, FanEntity, RestoreEntity):
    """A Crompton BLDC fan with assumed state."""

    _attr_name = None
    _attr_translation_key = "fan"
    _attr_speed_count = len(SPEED_KEYS)

    def __init__(self, entry: CromptonConfigEntry) -> None:
        """Initialize the fan."""
        super().__init__(entry)
        self._attr_unique_id = entry.entry_id
        self._attr_supported_features = (
            FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
            | FanEntityFeature.SET_SPEED
        )
        if self._remote.supports(CromptonKey.HYPER):
            self._attr_supported_features |= FanEntityFeature.PRESET_MODE
            self._attr_preset_modes = [PRESET_HYPER]
        self._is_on = False
        self._speed: CromptonKey | None = None
        self._preset: str | None = None

    @property
    def is_on(self) -> bool:
        """Return the assumed on/off state."""
        return self._is_on

    @property
    def percentage(self) -> int | None:
        """Return the assumed speed as a percentage."""
        if not self._is_on:
            return 0
        if self._preset is not None or self._speed is None:
            return None
        return ordered_list_item_to_percentage(SPEED_KEYS, self._speed)

    @property
    def preset_mode(self) -> str | None:
        """Return the assumed preset mode."""
        return self._preset

    async def async_added_to_hass(self) -> None:
        """Restore the last assumed state and follow sent keys."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            self._is_on = last_state.state == STATE_ON
            percentage = last_state.attributes.get(ATTR_PERCENTAGE)
            if isinstance(percentage, (int, float)) and percentage > 0:
                self._speed = percentage_to_ordered_list_item(SPEED_KEYS, percentage)
            if last_state.attributes.get(ATTR_PRESET_MODE) == PRESET_HYPER:
                self._preset = PRESET_HYPER
        self.async_on_remove(self._remote.async_add_listener(self._handle_key_sent))

    @callback
    def _handle_key_sent(self, key: CromptonKey) -> None:
        """Update the assumed state after a key was sent."""
        if key is CromptonKey.ON:
            self._is_on = True
        elif key is CromptonKey.OFF:
            self._is_on = False
            self._preset = None
        elif key in SPEED_KEYS:
            self._is_on = True
            self._speed = key
            self._preset = None
        elif key is CromptonKey.HYPER:
            self._is_on = True
            self._preset = PRESET_HYPER
        else:
            return
        self.async_write_ha_state()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on, optionally at a speed or in a preset."""
        if preset_mode is not None:
            keys = [CromptonKey.ON, CromptonKey.HYPER]
        elif percentage == 0:
            await self.async_turn_off()
            return
        elif percentage is not None:
            keys = [CromptonKey.ON, self._speed_key(percentage)]
        else:
            keys = [CromptonKey.ON]
        await self._remote.async_send(*keys, context=self._context)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self._remote.async_send(CromptonKey.OFF, context=self._context)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed, turning the fan on first if it is off."""
        if percentage == 0:
            await self.async_turn_off()
            return
        keys = [] if self._is_on else [CromptonKey.ON]
        keys.append(self._speed_key(percentage))
        await self._remote.async_send(*keys, context=self._context)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Enable the hyper preset, turning the fan on first if it is off."""
        keys = [] if self._is_on else [CromptonKey.ON]
        keys.append(CromptonKey.HYPER)
        await self._remote.async_send(*keys, context=self._context)

    @staticmethod
    def _speed_key(percentage: int) -> CromptonKey:
        return percentage_to_ordered_list_item(SPEED_KEYS, percentage)

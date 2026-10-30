"""Base entity for the Crompton BLDC RF Remote integration."""

from __future__ import annotations

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import Event, EventStateChangedData, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, MANUFACTURER
from .remote import CromptonConfigEntry


class CromptonEntity(Entity):
    """An entity of a Crompton fan, available while its transmitter is."""

    _attr_has_entity_name = True
    _attr_assumed_state = True
    _attr_should_poll = False

    def __init__(self, entry: CromptonConfigEntry) -> None:
        """Initialize the entity."""
        self._remote = entry.runtime_data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=self._remote.model.model,
        )

    async def async_added_to_hass(self) -> None:
        """Track the transmitter's availability."""
        await super().async_added_to_hass()
        transmitter = self._remote.transmitter_entity_id
        self._attr_available = self._transmitter_available()

        @callback
        def _transmitter_changed(event: Event[EventStateChangedData]) -> None:
            available = self._transmitter_available()
            if available != self._attr_available:
                self._attr_available = available
                self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [transmitter], _transmitter_changed
            )
        )

    def _transmitter_available(self) -> bool:
        state = self.hass.states.get(self._remote.transmitter_entity_id)
        return state is not None and state.state != STATE_UNAVAILABLE

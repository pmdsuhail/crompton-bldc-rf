"""RF command and sender for a Crompton BLDC fan remote."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from rf_protocols import ModulationType, RadioFrequencyCommand
import voluptuous as vol

from homeassistant.components.radio_frequency import async_send_command
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, Context, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .codes import CromptonKey, RemoteModel
from .const import COMMAND_DELAY, DOMAIN, FREQUENCY_HZ
from .protocol import FRAME_COUNT, encode_timings


class CromptonCommand(RadioFrequencyCommand):
    """One key press of the Crompton remote, as OOK timings."""

    def __init__(
        self,
        *,
        code: int,
        frequency: int = FREQUENCY_HZ,
        frame_count: int = FRAME_COUNT,
    ) -> None:
        """Initialize the command."""
        super().__init__(
            frequency=frequency, modulation=ModulationType.OOK, repeat_count=0
        )
        self.code = code
        self.frame_count = frame_count

    def get_raw_timings(self) -> list[int]:
        """Return signed microsecond timings (marks positive, spaces negative)."""
        return encode_timings(self.code, self.frame_count)


class CromptonRemote:
    """Sends remote keys through a radio_frequency transmitter entity."""

    def __init__(
        self, hass: HomeAssistant, transmitter_entity_id: str, model: RemoteModel
    ) -> None:
        """Initialize the remote."""
        self._hass = hass
        self._transmitter_entity_id = transmitter_entity_id
        self._model = model
        self._lock = asyncio.Lock()
        self._listeners: list[Callable[[CromptonKey], None]] = []

    @property
    def transmitter_entity_id(self) -> str:
        """Return the transmitter entity id."""
        return self._transmitter_entity_id

    @property
    def model(self) -> RemoteModel:
        """Return the fan model."""
        return self._model

    def supports(self, key: CromptonKey) -> bool:
        """Return True if the model has a code for this key."""
        return key in self._model.codes

    @callback
    def async_add_listener(
        self, listener: Callable[[CromptonKey], None]
    ) -> CALLBACK_TYPE:
        """Call ``listener`` with every key that was sent. Returns a remover."""
        self._listeners.append(listener)

        @callback
        def remove() -> None:
            self._listeners.remove(listener)

        return remove

    async def async_send(
        self, *keys: CromptonKey, context: Context | None = None
    ) -> None:
        """Send keys in order, waiting COMMAND_DELAY between them."""
        for key in keys:
            if not self.supports(key):
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="key_not_supported",
                    translation_placeholders={"model": self._model.model, "key": key},
                )
        async with self._lock:
            for index, key in enumerate(keys):
                if index:
                    await asyncio.sleep(COMMAND_DELAY)
                command = CromptonCommand(code=self._model.codes[key])
                try:
                    await async_send_command(
                        self._hass,
                        self._transmitter_entity_id,
                        command,
                        context=context,
                    )
                except vol.Invalid as err:
                    raise HomeAssistantError(
                        translation_domain=DOMAIN,
                        translation_key="transmitter_not_found",
                        translation_placeholders={
                            "entity_id": self._transmitter_entity_id
                        },
                    ) from err
                for listener in list(self._listeners):
                    listener(key)


type CromptonConfigEntry = ConfigEntry[CromptonRemote]

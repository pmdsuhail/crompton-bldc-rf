"""RF code table for Crompton BLDC fan remotes.

This is the one place to add codes. Each key maps to the 32-bit value that the remote
sends (see docs/protocol.md). Entities are only created for keys that have a code.

Pure module: stdlib imports only, so it can be loaded without Home Assistant.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final


class CromptonKey(StrEnum):
    """Keys on the physical Crompton BLDC remote."""

    ON = "on"
    OFF = "off"
    SPEED_1 = "speed_1"
    SPEED_2 = "speed_2"
    SPEED_3 = "speed_3"
    SPEED_4 = "speed_4"
    SPEED_5 = "speed_5"
    HYPER = "hyper"
    REVERSE_FORWARD = "reverse_forward"
    SLEEP = "sleep"
    TIMER_1H = "timer_1h"
    TIMER_2H = "timer_2h"
    TIMER_3H = "timer_3h"
    TIMER_4H = "timer_4h"


SPEED_KEYS: Final[tuple[CromptonKey, ...]] = (
    CromptonKey.SPEED_1,
    CromptonKey.SPEED_2,
    CromptonKey.SPEED_3,
    CromptonKey.SPEED_4,
    CromptonKey.SPEED_5,
)

# All keys in the order they appear on the remote.
BUTTON_KEYS: Final[tuple[CromptonKey, ...]] = (
    CromptonKey.ON,
    CromptonKey.OFF,
    *SPEED_KEYS,
    CromptonKey.HYPER,
    CromptonKey.REVERSE_FORWARD,
    CromptonKey.SLEEP,
    CromptonKey.TIMER_1H,
    CromptonKey.TIMER_2H,
    CromptonKey.TIMER_3H,
    CromptonKey.TIMER_4H,
)


@dataclass(frozen=True, slots=True)
class RemoteModel:
    """A fan model and the RF codes of its remote."""

    model_id: str
    model: str
    codes: Mapping[CromptonKey, int]


MODEL_CFENHP35W48IVYRM: Final = RemoteModel(
    model_id="cfenhp35w48ivyrm",
    model="CFENHP35W48IVYRM",
    codes={
        CromptonKey.ON: 0x91450E7A,
        CromptonKey.OFF: 0x91450641,
        CromptonKey.SPEED_1: 0x91450553,
        CromptonKey.SPEED_2: 0x91450F2E,
        CromptonKey.SPEED_3: 0x91450443,
        CromptonKey.SPEED_4: 0x91450311,
        CromptonKey.SPEED_5: 0x91450267,
        CromptonKey.HYPER: 0x91450C3C,
        # Not captured yet: learn with Broadlink, decode with decode_check.py, add here.
        # CromptonKey.REVERSE_FORWARD: 0x9145....,
        # CromptonKey.SLEEP: 0x9145....,
        # CromptonKey.TIMER_1H: 0x9145....,
        # CromptonKey.TIMER_2H: 0x9145....,
        # CromptonKey.TIMER_3H: 0x9145....,
        # CromptonKey.TIMER_4H: 0x9145....,
    },
)

MODELS: Final[dict[str, RemoteModel]] = {
    model.model_id: model for model in (MODEL_CFENHP35W48IVYRM,)
}

DEFAULT_MODEL: Final = MODEL_CFENHP35W48IVYRM.model_id

# Broadlink learned-command names (as stored by the user) -> remote key.
LEARNED_NAME_TO_KEY: Final[dict[str, CromptonKey]] = {
    "power": CromptonKey.ON,
    "Off": CromptonKey.OFF,
    "Speed1": CromptonKey.SPEED_1,
    "Speed2": CromptonKey.SPEED_2,
    "Speed3": CromptonKey.SPEED_3,
    "Speed4": CromptonKey.SPEED_4,
    "Speed5": CromptonKey.SPEED_5,
    "HYP": CromptonKey.HYPER,
}

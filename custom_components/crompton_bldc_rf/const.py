"""Constants for the Crompton BLDC RF Remote integration.

Pure module: stdlib imports only, so it can be loaded without Home Assistant.
"""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "crompton_bldc_rf"

CONF_TRANSMITTER: Final = "transmitter"
CONF_MODEL: Final = "model"

DEFAULT_NAME: Final = "Crompton Fan"
MANUFACTURER: Final = "Crompton"

# Nominal carrier of the remote (Broadlink captures report 433.84 to 434.00 MHz).
FREQUENCY_HZ: Final = 433_920_000

# Seconds between two keys sent in one sequence (for example ON, then a speed).
COMMAND_DELAY: Final = 0.8

PRESET_HYPER: Final = "hyper"

# Original codes learned by a Broadlink RM4 Pro, keyed by model id and learned name.
# Kept for reference only and not transmitted: the integration regenerates clean frames
# from the 32-bit codes in codes.py. See docs/protocol.md.
BROADLINK_LEARNED_CODES: Final[dict[str, dict[str, str]]] = {
    "cfenhp35w48ivyrm": {
        "Speed2": (
            "scBYAbqeBgA6CAoYChkaCAkZChkJGRoJCRkaCQkZCRkJGRoJCRkaCQgaCRkJGQkaGQkaCRkJ"
            "GgkJGggaGQkJGRsIGQkaCQgaCAABGRoJCRkJGRsICRkJGQoZGggJGhoICRkJGgkZGggJGRoJ"
            "CRkJGQoZCRkaCRoIGgkZCggaCRkaCQgaGggaCRkJCRkJAAEZGggJGgkZGggJGgkZCRkaCQkZ"
            "GgkJGQkZCRkaCQkZGgkIGgkZCRkJGhoIGgkaCBoJCRoIGhkJCRoZCRoIGgkIGgkAARgbCAkZ"
            "CRkbCAkZCRoJGRoIChkaCAkZCRoJGRoJCRkaCAkaCRkJGQkZGwgaCRkJGgkJGQkaGQkJGRoJ"
            "GQkZCQkZCQABGRoJCRkJGRoJCRkJGQkaGggJGRsICRkJGgkZGggJGRoJCRkJGQkaCRkaCRoI"
            "GgkZCggaCRkaCQgaGggaCRkJCBoJAAXc"
        ),
        "power": (
            "scBaAbqeBgAEHRsICRkJGRsICRkJGQoZGggJGRoJCRkKGQkZGggJGhkJCRkJGggaCRkaCRkJ"
            "GgkIGgkaGQkZCRoJGQkIGhkKCBoIAAEZGgkJGQkZGgkJGQkZCRoaCAkaGQkJGQkZChkaCAkZ"
            "GgkJGQkZCRoIGhoIGgkaCQgaCRkaCRkJGgkZCQgaGggJGggAARkaCQkZCRkaCQkZCRkJGRsI"
            "CRoZCQkZCRkJGhoICRkaCQkZCRkJGgkZGggaCRoICRoJGRoJGQkaCRkJCBoaCAkaCAABGRoI"
            "CRoJGRoICRoJGQkaGQkJGRoJCBoJGQkZGgkJGRoICRoIGgkZCRkbCBoJGQkJGgkZGggaCRkJ"
            "GggJGhkJCRkJAAEYGgkJGQkZGwgJGQkaCRkaCQkZGggJGgkZCRkaCAkaGggJGQkaCRkJGRoJ"
            "GggaCQgaCRoZCRoIGgkZCQkaGQkIGgkABdw="
        ),
        "Off": (
            "scBgAQqfBgAAAp0ABK0FHBsIChgKGRoICRkKGQkZGgkJGRoICRoJGQkZGgkIGhoICRoIGgkZ"
            "CRkJGhoIGgkIGgkaGQkJGQkaCBoJGQkZGgkJAAEYGgkJGQkZGgkJGQkZCRoaCAkZGgkJGQkZ"
            "ChkaCAkZGgkJGQkZCRoJGQkZGgkaCAkaCRkaCQgaCRkJGQkaCRkaCAkAARkaCAoZCRkaCQkZ"
            "CRkJGhoICRkaCQkZCRkJGhkJCRkaCQgaCRkJGQoZCRkaCRoICRoJGRoJCBoJGQkZCRoJGRoI"
            "CQABGRoICRoJGRoICRoJGQkZGgkJGRoJCRkJGQkZGgkJGRoJCBoJGQkZCRoJGRoIGgkJGgkZ"
            "GggJGggaCRkJGQkaGggJAAEZGggJGQoZGggJGgkZCRkaCQkZGggJGgkZCRkaCQkZGggJGgkZ"
            "CRkJGgkZGggbCAkaCRkaCAkZCRoJGQkZCRoaCAkABdw="
        ),
        "Speed1": (
            "ssBcAVCfBgAAA4AdGwgJGQoYGwgJGQkaCRkaCQkZGggJGQkaCRkaCAkaGQkJGQkaCRkJGQka"
            "GggJGhkJCRoZCQkZGgkIGgkZGgkZCQkAARkaCAkZCRoaCAkZCRoJGRoJCRkaCAkaCRkJGRoJ"
            "CRkaCAkaCBoJGQkZCRoaCAkaGQkJGhoICRkaCQkZCRkaCRkJCQABGRoICRkJGhoICRkKGQkZ"
            "GgkJGRoICRoJGQkZGgkJGRoJCBoJGQkZCRoJGRoICRoaCQkZGggJGhkJCRkJGRoJGQkJAAEZ"
            "GggJGQkaGggJGgkZCRkaCQkZGgkJGQkZCRoZCQkZGgkIGgkZCRkJGgkZGggJGhoJCRkaCAka"
            "GQkJGQkaGQkaCAkAARkaCAkaCRkaCQgaCRkJGRoJCRkaCAkaCRkJGhkJCRkaCQkZCRkJGgga"
            "CRkaCQgaGgkJGRoICRoZCQkZCRoZCRoICQAF3A=="
        ),
        "Speed3": (
            "scDgAc6eBgAEAAU1CAAFMAwAApQJAAKWDAACkQUAApoMAAKTDAACkg0AApoFAAKTCwACkgwA"
            "ApMMAAKSDAACkwwAApIEBAYAAcQEHRsICRkKGRoICRkKGQkZGgkJGRoICRoJGQkZGgkJGRoI"
            "CRoIGgkZCRoJGRoJCBoJGggaGggJGQkaCRkJGRoJGQkJAAEZGggJGQkaGggJGQoZCRkaCQkZ"
            "GgkJGQkZCRkaCQkZGgkIGgkZCRkJGgkZGgkIGgkZChkaCAkZChkJGQkaGQkaCAkAARkaCAka"
            "CRkaCAoZCRkJGRoJCRkaCQkZCRkJGRoJCRkaCQkZCRkJGgkZCRkaCQkZCRoJGRoICRoJGQkZ"
            "CRoaCBoICQABGRoIChkJGRoJCRkJGQkaGggJGhoICRkJGQoZGggJGRoJCRkJGQkaCRkJGRoJ"
            "CRkJGgkZGgkJGQkZCRoJGRoIGgkJAAEYGgsHGQkZGwgJGQkZChkaCAkaGggJGQoZCRkaCAoZ"
            "GggJGggaCRkJGQkaGggJGQkaCRkaCQkZCRkJGgkZGggaCQkAARkaCAkZChkaCAkZChkJGRoJ"
            "CRkaCAkaCRkJGRoJCRkaCAkaCBoJGQkZCRoaCAkaCRkKGRoICRkJGgkZCRkaCRoICQAF3A=="
        ),
        "Speed4": (
            "scAYAbCeBgAbCAkZCRkbCAkZCxgJGRoJCRkaCAkaCRkJGRoJCBoaCQgaCRkJGQkaCRkJGRoJ"
            "GgkJGQkZCRoZCQkZCRoJGRoICQABGRoJCRkJGRoJCRkJGQkaGggJGhoICRkJGQoZGggJGRoJ"
            "CRkJGQkaCRkJGQkaGggaCQkaCRkJGRoJCBoJGQkZGgkJAAEYGwgJGQkaGggJGQoZCRkaCQkZ"
            "GgkIGgkZCRkaCQkZGgkIGgkZCRkJGgkZCRkaCRoJCRkJGQoZGggJGQkaCRkaCAkAARkaCQkZ"
            "CRkaCQkZCRkJGhoICRkaCQkZCRkJGhoICRkaCQkZCRoIGgkZCRkKGRoIGgkJGQkaCRkaCAka"
            "CRkJGRoJCQADpQQABdw="
        ),
        "Speed5": (
            "scBYAcSeBgAdBwoZCRkaCAoZCRkLGBoICRoZCQkZCRkKGRoICRkaCQkZCRoIGgkZCRkJGhoI"
            "CRoJGRoJGQkJGQkZGgkaCBoJCAABGRsICRkJGRsICRkJGQoZGggKGRoICRkJGgkZGggJGhoI"
            "CRkJGgkZCRkJGgkZGgkJGQkaGQkaCAkaCRkaCBoJGQkJAAEYGwgJGQkZGwgJGgkZCRkaCQkZ"
            "GggJGgkZCRkaCQkZGggJGgkZCRkJGgkZCRkaCQkaCBoaCBoJCBoJGRoIGgkZCQkAARgbCAkZ"
            "CRoaCAkZCRoJGRoJCRkaCAkZChkJGRoIChkaCAkaCRkJGQkZCRoJGRoJCRkJGhoIGggJGgkZ"
            "GggaCRkJCQABGBoJCRkJGhoICRkJGgkZGgkJGRoICRkKGQkZGggJGhoICRkJGgkZCRkJGgkZ"
            "GggKGQkaGggaCAkaCRkaCBoJGQkJAAXc"
        ),
        "HYP": (
            "scAUAc6eBgAbCAkZChgbCAkZChkJGRoJCRkaCAkaCRkJGRoICRoZCQkZCRoJGQkZGgkaCQga"
            "CRoIGgkZGggaCRkJGgkIGggaCQABGBsICRkJGRsICRkJGgkZGgkJGRoICRoJGQkZGgkIGhoI"
            "CRoIGgkZCRkaCRoICRoJGQkaCRkaCBoJGQkaCQgaCRkJAAEZGggJGQkaGggJGQoZCRkaCQkZ"
            "GggJGgkZCRkaCQgaGggJGgkZCRkJGhoIGgkIGgkaCRkJGRoIGgkaCBoJCBoJGQkAARkaCAkZ"
            "ChkaCAkZChkJGRoJCRkaCAkaCRkJGRoJCRkaCAkaCRkJGQkaGggaCQgaCRoIGgkZGgkZCRoI"
            "GgkIGgkZCQAF3A=="
        ),
    },
}

"""Timing generator for the Crompton BLDC RF remote protocol.

Each frame is 32 data bits, MSB first (1 = long mark + short space, 0 = short mark +
long space), then a short stop mark and a long inter-frame gap. See docs/protocol.md.

Timings are signed microseconds: marks positive, spaces negative.

Pure module: stdlib imports only, so it can be loaded without Home Assistant.
"""

from __future__ import annotations

from typing import Final

SHORT_US: Final = 270
LONG_US: Final = 780
GAP_US: Final = 8550
CODE_BITS: Final = 32
FRAME_COUNT: Final = 6


def encode_frame(code: int) -> list[int]:
    """Return the 66 timings of one frame: 32 bit pairs, stop mark and gap."""
    if not 0 <= code < 1 << CODE_BITS:
        raise ValueError(f"code must be a {CODE_BITS}-bit unsigned integer: {code!r}")
    timings: list[int] = []
    for bit in range(CODE_BITS - 1, -1, -1):
        if (code >> bit) & 1:
            timings += (LONG_US, -SHORT_US)
        else:
            timings += (SHORT_US, -LONG_US)
    timings += (SHORT_US, -GAP_US)
    return timings


def encode_timings(code: int, frame_count: int = FRAME_COUNT) -> list[int]:
    """Return a full transmission: a lead-in gap, then ``frame_count`` frames."""
    if frame_count < 1:
        raise ValueError(f"frame_count must be at least 1: {frame_count!r}")
    return [SHORT_US, -GAP_US] + encode_frame(code) * frame_count

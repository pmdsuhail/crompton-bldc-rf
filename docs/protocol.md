# Crompton BLDC RF remote protocol (model CFENHP35W48IVYRM)

This document records how the RF codes for the Crompton CFENHP35W48IVYRM ceiling fan
remote were decoded from Broadlink captures, and how the integration regenerates them.

Source data: eight codes learned by the user with a Broadlink RM4 Pro (`power`, `Off`,
`Speed1`..`Speed5`, `HYP`). Exploration scripts are in `.agents/tasks/decode_explore*.py`
(not shipped). The repeatable check is `.agents/tasks/decode_check.py`.

## 1. Broadlink packet format seen in the captures

| Offset | Size | Value in captures | Meaning |
|---|---|---|---|
| 0 | 1 | `0xB1` (7 codes), `0xB2` (`Speed1`) | RF 433 MHz. `0xB1` is what an RM4 Pro returns for a 433 MHz capture. |
| 1 | 1 | `0xC0` in every capture | Not a repeat count for RM4 Pro captures. The device ignores the packet if it is set to 0. |
| 2..3 | 2 | e.g. `0x0158` | Payload length, little-endian, counted from offset 4. |
| 4..7 | 4 | 433840..434000 | Carrier the capture was learned on, in kHz, little-endian. |
| 8.. | n | | Durations in Broadlink ticks. One byte per duration; `0x00 hi lo` means a big-endian 16-bit tick count. |
| end | | `... 0x05 0xDC` | Last duration is `0x05DC` = 1500 ticks (end-of-capture silence). |

Even `Speed1` (`0xB2`) carries the 4-byte carrier field, so all eight captures decode with
the timings starting at offset 8. The `broadlink_async` library documents the same RM4 Pro
layout (8-byte header for `0xB1`).

Tick length: 8192/269 µs ≈ 30.453 µs (`broadlink_async.remote.TICK`, used by Home
Assistant's Broadlink `radio_frequency` platform since 2026.10). Home Assistant 2026.5
through 2026.9 encoded with 32.84 µs ticks instead; see section 6.

Carrier: the captures report 433.84 to 434.00 MHz. That is the RM4 Pro's frequency-sweep
estimate of a nominal 433.92 MHz remote. The integration transmits at **433 920 000 Hz, OOK**.

## 2. Frame structure

Each capture holds a run of identical frames (4 to 6). Each frame is:

```
32 data bits, MSB first
  bit 1 = long mark  + short space
  bit 0 = short mark + long space
stop mark (short)
inter-frame gap (long space)
```

Timing statistics over the 31 frames that are followed by a regular 280/281-tick gap
(628 zero bits, 364 one bits). The last frame of each capture ends in the 1500-tick
end-of-capture silence instead, so it is decoded but left out of the gap statistics. In total
39 frames decode.

| Element | Mean ticks | SD | µs (×30.453) | Chosen value (µs) |
|---|---|---|---|---|
| short mark (bit 0) | 8.98 | 0.41 | 273.5 | 270 |
| long space (bit 0) | 25.31 | 0.48 | 770.8 | 780 |
| long mark (bit 1) | 26.02 (median 26) | 1.75* | 792.5 | 780 |
| short space (bit 1) | 8.56 | 0.53 | 260.8 | 270 |
| stop mark | 8.84 | 0.37 | 269.2 | 270 |
| inter-frame gap | 280.71 | 0.45 | 8548.6 | 8550 |

\* One corrupted 58-tick mark at the start of the `Speed2` capture inflates the SD; every
other long mark is 24..27 ticks.

Base unit T ≈ 262 µs: short ≈ 1T, long ≈ 3T, bit period ≈ 4T (≈ 1.05 ms), gap ≈ 32.6T.
This is the common EV1527/PT2262-style pulse-width encoding stretched to 32 bits, with the
sync gap placed after a stop pulse. Frame length: 32 × 1.05 ms + 0.27 ms + 8.55 ms ≈ 42.4 ms.

## 3. Decoded codes

Every clean frame inside each capture decodes to the same 32-bit value.

| Remote key | Broadlink name | Type byte | Carrier (kHz) | Clean frames | 32-bit code | Upper 16 bits | Lower 16 bits |
|---|---|---|---|---|---|---|---|
| ON | `power` | `0xB1` | 433850 | 5 | `0x91450E7A` | `0x9145` | `0x0E7A` |
| OFF | `Off` | `0xB1` | 433930 | 5 | `0x91450641` | `0x9145` | `0x0641` |
| 1 | `Speed1` | `0xB2` | 434000 | 5 | `0x91450553` | `0x9145` | `0x0553` |
| 2 | `Speed2` | `0xB1` | 433850 | 5 | `0x91450F2E` | `0x9145` | `0x0F2E` |
| 3 | `Speed3` | `0xB1` | 433870 | 6 | `0x91450443` | `0x9145` | `0x0443` |
| 4 | `Speed4` | `0xB1` | 433840 | 4 | `0x91450311` | `0x9145` | `0x0311` |
| 5 | `Speed5` | `0xB1` | 433860 | 5 | `0x91450267` | `0x9145` | `0x0267` |
| HYP (Hyper) | `HYP` | `0xB1` | 433870 | 4 | `0x91450C3C` | `0x9145` | `0x0C3C` |

Capture artifacts, which the regenerated frames drop:

- `power`, `Off`, `Speed1`: one or two noise durations before the first frame (e.g. `Off`
  starts with a 669-tick mark and a 1197-tick space).
- `Speed3`: about 15 unrelated pulses with ~20 ms spacing before the first frame.
- `Speed2`: the first mark is 58 ticks instead of ~26 (capture started mid-pulse).
- `Speed4`: the last frame is followed by a 933-tick gap and a stray 4-tick mark.

## 4. Address / command split

- Bits 31..16 are `0x9145` in all eight codes. Bits 15..12 are `0` in all eight codes.
  The common prefix is therefore at least 20 bits (`0x91450`).
- The low 12 bits vary per key. The nibble at bits 11..8 looks like a key number
  (`E` ON, `6` OFF, `5`/`F`/`4`/`3`/`2` speeds 1..5, `C` HYP), but the low byte has no
  relationship to the other bytes that I could find:
  - no CRC-8 matches (all 256 polynomials × 256 init values × reflected/unreflected input and
    output, with a free final XOR, over bytes 0..2 or byte 2 alone);
  - no 8-bit sum or XOR of the first three bytes, and no sum, difference or XOR with byte 2,
    matches.
- Conclusion: treat `0x9145` as the remote/fan address and the low 16 bits as an opaque
  per-key command. Codes for keys that were not captured (R/F, SLEEP, 1H, 2H, 3H, 4H)
  **cannot be derived** and are not invented. They must be learned and added to the code
  table.

The user reports that these codes work for any fan of this model. That is plausible
(the remote has no pairing procedure that the user mentioned), but it is not verified.

## 5. Chosen approach: generate frames from the 32-bit code

The bit decode is clean (every frame of every capture agrees, timing SD below 0.6 tick), so
the integration stores one 32-bit code per key and generates the timings. It does not replay
the raw captures. This drops the capture noise listed in section 3 and makes new keys a
one-line addition.

Generated transmission (signed microseconds, marks positive, spaces negative, the
`rf_protocols` / Flipper RAW convention):

```
lead-in:  +270, -8550                      (stop mark + gap, so frame 1 is preceded by a gap)
frame × 6:
  for each of the 32 bits, MSB first:
    1 -> +780, -270
    0 -> +270, -780
  +270, -8550                              (stop mark + inter-frame gap)
```

Six frames is the most seen in a capture. That is about 0.26 s of transmission, close to a
short key press. `repeat_count` on the command is 0 because the frames are already in the
timing list. That keeps the result the same on transmitters that handle `repeat_count`
differently.

Length: 2 + 6 × 66 = 398 durations. With Broadlink's encoder this is 398 bytes plus 2 extra
bytes for each 8550 µs gap (more than 255 ticks), about 412 bytes in total, which is within
the size of the learned packets.

## 6. Transmitter tick caveat

Home Assistant's Broadlink `radio_frequency` platform converts microseconds to ticks with
`round(us / tick)`:

| HA version | Tick used | 270 µs -> | 780 µs -> | 8550 µs -> | Effect on air |
|---|---|---|---|---|---|
| 2026.10+ (`broadlink_async.TICK`) | 30.453 µs | 9 | 26 | 281 | Same tick counts as the learned codes |
| 2026.5 to 2026.9 | 32.84 µs | 8 | 24 | 260 | About 7% shorter than the remote's timing |

Ratio-based pulse-width decoders like EV1527 usually tolerate a 7% uniform compression, but
this has not been tested on the fan. If the fan does not respond on an older HA version,
updating HA is the first thing to try.

## 7. Confidence

| Claim | Confidence | Basis |
|---|---|---|
| Frame structure, bit encoding, 32-bit values per key | High | 39 frames decode identically within each capture; tight timing statistics |
| Generated timings match the learned ones | High | `decode_check.py` asserts every generated duration is within 15% of the per-position median of the learned frames |
| The fan accepts the regenerated frames | Medium-high | Timings and structure match the captures. Not yet tested on hardware |
| `0x9145` is shared by all CFENHP35W48IVYRM remotes | Medium | User statement only |
| Meaning of HYP | Medium | Not printed on the remote photo. The name suggests a hyper/boost mode |
| Codes for R/F, SLEEP, 1H..4H | None | Not captured and not derivable (section 4) |

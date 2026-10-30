# Crompton BLDC RF Remote

A Home Assistant custom integration that controls a Crompton BLDC ceiling fan through a
433.92 MHz RF transmitter. It works like the core `led_infrared` and `novy_cooker_hood`
integrations: the remote's codes ship with the integration, and you get a device with a
fan entity and one button per remote key. You don't need to learn or paste codes.

Supported model: **CFENHP35W48IVYRM**. The codes are expected to work for every fan of
this model (not verified on more than one fan).

Your remote should look like this: ON and OFF at the top, a speed ring 1 to 5, Sleep and
HYP, and 1H to 4H timer keys. Every key is supported.

<img src="https://raw.githubusercontent.com/pmdsuhail/crompton-bldc-rf/main/docs/remote.svg" alt="Crompton CFENHP35W48IVYRM remote layout: ON, OFF, speeds 1-5, Sleep, HYP, 1H-4H timers" width="160">

This project is not affiliated with Crompton Greaves Consumer Electricals Limited.

## Requirements

- Home Assistant **2026.5.0** or newer (the first release with the `radio_frequency`
  integration). With a Broadlink transmitter, **2026.10 or newer is recommended**: older
  versions send the pulses about 7% shorter than the original remote. See
  [docs/protocol.md, section 6](docs/protocol.md#6-transmitter-tick-caveat).
- A device that provides a `radio_frequency` transmitter entity covering 433.92 MHz with
  OOK modulation, for example a Broadlink RM4 Pro or an ESPHome RF transmitter. Set it up
  in Home Assistant first. Check that it shows up as a `radio_frequency.*` entity.

## Installation

### HACS (custom repository)

1. In HACS, open the three-dot menu and choose **Custom repositories**.
2. Add `https://github.com/pmdsuhail/crompton-bldc-rf` with category
   **Integration**.
3. Search for **Crompton BLDC RF Remote**, download it, and restart Home Assistant.

### Manual

Copy `custom_components/crompton_bldc_rf` into the `custom_components` folder of your Home
Assistant configuration, then restart Home Assistant.

## Setup

1. Go to **Settings → Devices & services → Add integration** and pick
   **Crompton BLDC RF Remote**.
2. Enter a name for the fan (default "Crompton Fan").
3. Pick the radio frequency transmitter. Only transmitters that support 433.92 MHz OOK are
   listed.

Repeat this for each fan. Every fan becomes its own device. You can use the same
transmitter for several fans as long as each one has a different name. Note that fans of
the same model share the same codes, so one key press reaches every such fan in range.

## Entities

Each fan device (manufacturer Crompton, model CFENHP35W48IVYRM) has:

| Entity | What it does |
|---|---|
| Fan | On/off, speeds 1 to 5 (20% steps), preset `hyper` |
| Button **On** | Sends the ON key |
| Button **Off** | Sends the OFF key |
| Buttons **Speed 1** to **Speed 5** | Send the speed keys |
| Button **Sleep** | Sends the SLEEP key (the fan lowers its speed over time) |
| Button **Hyper** | Sends the HYP key (hyper mode) |
| Buttons **Timer 1 hour** to **Timer 4 hours** | Send the 1H to 4H off-timer keys |

Every key on the remote is covered. Sleep and the timers don't change the fan entity's
state: when a timer turns the fan off, Home Assistant can't see it, so the fan entity
still shows on.

Fan behavior:

- **Turn on** without a speed sends ON. The fan uses its own last speed.
- **Turn on** with a speed sends ON, waits 0.8 s, then sends the speed key.
- **Set speed** sends the speed key. If the integration thinks the fan is off, it sends ON
  first.
- **Preset hyper** sends HYP, with ON first if the fan is believed to be off.
- **Turn off** sends OFF.

RF is one-way, so the fan entity uses an **assumed state**. It tracks the keys that Home
Assistant sent, including button presses, and restores that state after a restart. It
cannot see presses on the physical remote, so the state can drift if you also use the
remote. The entities are unavailable while the transmitter entity is unavailable.

## How to add codes for another key or remote

Key codes cannot be derived from each other (see
[docs/protocol.md, section 4](docs/protocol.md#4-address--command-split)), so each one has
to be learned. If you capture codes for another Crompton remote, please open an issue or
pull request with the Broadlink codes.

### 1. Learn the key with Broadlink

1. Go to **Developer tools → Actions** and run `remote.learn_command` on your Broadlink
   remote entity with:
   ```yaml
   action: remote.learn_command
   target:
     entity_id: remote.your_broadlink
   data:
     device: crompton_fan
     command: sleep
     command_type: rf
   ```
2. Follow the notification: hold the key until the frequency is found, release, then press
   it once more.
3. The learned code (base64) is stored in `.storage/broadlink_remote_<mac>_codes` in your
   configuration folder.

### 2. Decode it to a 32-bit code

Each capture contains several identical 32-bit frames. Every bit is a short/long pulse
pair: a long mark followed by a short space is 1, a short mark followed by a long space is
0, MSB first. The full procedure is in [docs/protocol.md](docs/protocol.md). The decoder
in this repository's development tools (`decode_check.py`) prints the code for each
captured key. All known codes for CFENHP35W48IVYRM start with `0x9145`.

### 3. Add one line to the code table

In `custom_components/crompton_bldc_rf/codes.py`, add the key to `MODEL_CFENHP35W48IVYRM`:

```python
        CromptonKey.NEW_KEY: 0x9145XXXX,
```

A new key also needs an entry in `CromptonKey` and `BUTTON_KEYS` in `codes.py`, a name in
`strings.json` and `translations/en.json`, and an icon in `icons.json`. Restart Home
Assistant and the button appears.

### Adding another fan model

Add a `RemoteModel` to `codes.py`, register it in `MODELS`, and add its option label under
`selector.model.options` in `strings.json` and `translations/en.json`. With more than one
model, the setup dialog shows a model dropdown.

## Troubleshooting

- **The fan does not react.** Move the transmitter closer to the fan. On Broadlink with
  Home Assistant older than 2026.10, update Home Assistant first (pulse timing, see
  above). Check that the original remote still works.
- **"No radio frequency transmitter found" during setup.** Set up the Broadlink or ESPHome
  device first and check that it provides a `radio_frequency` entity.
- **Entities are unavailable.** The transmitter entity is unavailable. Check the Broadlink
  or ESPHome device.
- **Turn on with a speed only turns the fan on.** The fan may need more time between the ON
  and speed keys. Increase `COMMAND_DELAY` in `const.py`.

## Protocol

The RF protocol and how the codes were decoded are documented in
[docs/protocol.md](docs/protocol.md).

## License

MIT, see [LICENSE](LICENSE).

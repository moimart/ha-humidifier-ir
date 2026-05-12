# Humidifier IR Remote — Home Assistant custom integration

Drive a one-way IR-controlled humidifier from Home Assistant via any IR
transmitter exposed under the HA 2026.4 `infrared` entity platform —
Broadlink RM4 / RM4 Pro / RM Mini, ESPHome IR blasters, etc.

Codes are stored symbolically (NEC at address `0x00`) and encoded via
[`infrared-protocols`](https://github.com/home-assistant-libs/infrared-protocols),
so they're portable across any compatible transmitter — no Broadlink
base64 blobs.

## What you get per humidifier

One device with four entities:

| Entity | Purpose |
|---|---|
| `humidifier.<name>` | Power on/off + mode (Continuous / Intermittent) |
| `button.<name>_light` | One-press: toggle the unit's night light |
| `button.<name>_mist_level` | One-press: toggle mist level (low ↔ high) |
| `button.<name>_cycle_timer` | One-press: advance the unit's timer setting |

All entities are **`assumed_state`** — there's no feedback channel from
the humidifier, so HA's state tracks what we *think* the unit is doing.
If someone uses the physical remote, HA's state drifts until you sync it
manually.

## Requirements

- Home Assistant Core **≥ 2026.4** (for the `infrared` entity platform)
- An IR transmitter integration set up and exposing an `infrared.*` entity

## Install via HACS

1. HACS → ⋮ → **Custom repositories** → URL: `https://github.com/moimart/ha-humidifier-ir`, Type: **Integration** → **Add**.
2. Click the new card → **Download** → pick `v0.1.0`.
3. **Settings → System → Restart Home Assistant**.
4. **Settings → Devices & Services → + Add Integration → "Humidifier IR Remote"**.
5. Name the humidifier and pick the IR transmitter that has line-of-sight to it.

## Capture codes for *your* humidifier

This release ships codes for a 6-button remote with `onoff / intermittent / continuous / timing / bigsmall / light`. If your remote layout matches but the bytes are different, capture with Broadlink's `remote.learn_command` and patch `custom_components/humidifier_ir_remote/codes.py`.

## Known limitations

- **One-way only.** State is assumed; physical remote usage causes drift. Reselecting a mode (`humidifier.set_mode`) resynchronises that one bit.
- **Power is a toggle.** The remote has a single power button. `turn_on` while we think we're already on does nothing; same for `turn_off`. If state drifts, HA's toggle might do the opposite of what you want — manual sync via the physical remote may be needed.
- **No humidity target.** `target_humidity` isn't supported; the bulb has no sensor and no way to set a specific humidity level.
- **Timer is opaque.** The cycle-timer button advances through the unit's timer presets, but we don't know which one is active.

## License

MIT.

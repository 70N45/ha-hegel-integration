# CLAUDE.md

Development guide for the Hegel H590 Home Assistant integration.

## Project Structure

```
custom_components/hegel_h590/
  __init__.py        # Entry point: stores shared amp in hass.data, forwards platforms based on mode
  const.py           # Domain, port, source map, mode constants
  config_flow.py     # UI setup: name, host, port, sources, mode selection
  hegel_backend.py   # HegelAmp class: TCP socket protocol (power, volume, source, mute)
  media_player.py    # HegelH590Receiver entity (device_class: receiver) for HomeKit accessory mode
  fan.py             # HegelVolumeFan entity (workaround: volume as fan speed %)
  select.py          # HegelSourceSelect entity (workaround: input as dropdown)
  switch.py          # HegelPowerSwitch entity (workaround: power as switch)
  hegel.py           # Standalone test script (hardcoded IP, manual protocol testing)
  manifest.json      # Integration metadata (domain, version, iot_class)
hacs.json            # HACS repository metadata
```

## Architecture

### Data Flow

1. `__init__.py` creates a shared `HegelAmp` instance and stores it in `hass.data[DOMAIN][entry_id]`
2. Based on the configured `mode` (receiver/workaround/both), it forwards setup to the appropriate platforms
3. Each platform's `async_setup_entry` pulls the shared amp and source config from `hass.data`
4. All entities use `async_update()` for polling (iot_class: local_polling) and `async_write_ha_state()` after commands

### Hegel Protocol

TCP socket on port 50001. Commands are ASCII with `\r` terminator. Each command opens a new connection (no persistent socket). Responses are in the format `-<cmd>.<value>`.

Key backend methods on `HegelAmp`:
- `get_power()` / `set_power(bool)` — `-p.?` / `-p.0` / `-p.1`
- `get_volume()` / `set_volume(int)` — `-v.?` / `-v.<0-100>`
- `get_source()` / `set_source(int)` — `-i.?` / `-i.<1-12>`
- `get_mute()` / `set_mute(bool)` — `-m.?` / `-m.0` / `-m.1`

### HomeKit Integration Modes

The `mode` config option determines which entity platforms are loaded:

| Mode | Platforms | Use Case |
|------|-----------|----------|
| `receiver` | `media_player` | Best UX — native HomeKit Receiver with volume/source/mute. Requires accessory mode. |
| `workaround` | `fan`, `select`, `switch` | Works in bridge mode. Amp appears as 3 separate devices. |
| `both` | All four | For testing or mixed use. |

The receiver approach works because HA's HomeKit bridge maps `device_class: receiver` to HomeKit's Television/Receiver accessory (category 34), which has native input source services and a TelevisionSpeaker linked service for volume control.

## Key Design Decisions

- **Single amp instance shared via hass.data** — avoids multiple TCP connections polling the same device
- **device_class RECEIVER over TV** — semantically correct for an amplifier, same HomeKit capabilities
- **No persistent TCP connection** — the Hegel protocol is simple request/response; a new socket per command avoids stale connection issues
- **Volume step = 5** — used for volume_up/volume_down on the receiver entity (Apple Remote widget buttons)
- **Fan speed_count = 100** — gives 1% granularity, maps directly to Hegel's 0-100 volume range

## Testing

No automated test suite. Manual testing against the physical amp:

```bash
# Quick protocol test (edit IP in hegel.py first)
python3 custom_components/hegel_h590/hegel.py
```

For HA integration testing, add the component via the UI and verify:
1. Power on/off from HA dashboard
2. Volume slider responds
3. Source selection works
4. States update when changed via physical remote
5. HomeKit exposure shows correct controls for the configured mode

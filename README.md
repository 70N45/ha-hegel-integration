# Hegel H590 Home Assistant Integration

Custom Home Assistant integration for the **Hegel H590** amplifier, providing control over TCP/IP (port 50001). Designed with HomeKit compatibility in mind.

## Features

- **Power** on/off
- **Volume** control (0–100)
- **Input source** switching (12 inputs: XLR, Phono, Coax, Optical, USB, Network, etc.)
- **Mute** toggle
- **HomeKit** support via three configurable modes

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS
2. Install "Hegel H590"
3. Restart Home Assistant
4. Go to **Settings → Devices & Services → Add Integration → Hegel H590 Amplifier**

### Manual

Copy the `custom_components/hegel_h590` folder into your Home Assistant `custom_components` directory and restart.

## Configuration

During setup you'll be asked for:

| Field | Description |
|-------|-------------|
| **Name** | Display name (default: "Hegel H590") |
| **Host** | IP address of the amp on your network |
| **Port** | TCP port (default: 50001) |
| **Sources** | Which inputs to expose (multi-select) |
| **Mode** | How to expose the amp to HomeKit (see below) |

## HomeKit Modes

### `receiver` (recommended)

Creates a single `media_player` entity with `device_class: receiver`. Home Assistant's HomeKit bridge maps this to a **Receiver accessory** (HomeKit category 34), which natively provides:

- Power on/off
- Volume slider + step (up/down via Apple Remote widget)
- Mute toggle
- Input source dropdown
- Apple Remote widget in iOS Control Center

**Requirement:** The entity must be exposed in **HomeKit accessory mode** — create a separate HomeKit Bridge instance (Settings → Devices & Services → Add Integration → HomeKit Bridge) and include only this entity.

### `workaround`

Creates three separate entities that work in **HomeKit bridge mode** (no separate bridge needed):

| Entity | Type | HomeKit exposure |
|--------|------|-----------------|
| *Name* Volume | `fan` | Speed slider = volume (0–100%) |
| *Name* Input | `select` | Dropdown for input source selection |
| *Name* Power | `switch` | On/off toggle |

Use this if you can't or don't want to set up accessory mode. The tradeoff is that your amp appears as three separate devices in HomeKit rather than one cohesive receiver.

### `both`

Creates all four entities (receiver + fan + select + switch). Useful for experimenting to see which works best in your HomeKit setup, or if you want the receiver entity for HA dashboards and the workaround entities for HomeKit bridge mode.

## Hegel Protocol

The integration communicates with the H590 over TCP on port 50001 using ASCII commands:

| Command | Description |
|---------|-------------|
| `-p.?` | Query power state |
| `-p.0` / `-p.1` | Power off / on |
| `-v.?` | Query volume (0–100) |
| `-v.<n>` | Set volume |
| `-i.?` | Query input (1–12) |
| `-i.<n>` | Set input |
| `-m.?` | Query mute |
| `-m.0` / `-m.1` | Unmute / mute |

Reference: [Hegel H590 IP Control Codes](https://support.hegel.com/component/jdownloads/send/3-files/14-h590-ip-control-codes)

## Available Inputs

| Name | ID | Name | ID |
|------|----|------|----|
| Xlr1 | 1 | Bnc | 6 |
| Xlr2 | 2 | Coax | 7 |
| Heimkino | 3 | Opt1 | 8 |
| Phono | 4 | Opt2 | 9 |
| Analog3 | 5 | Opt3 | 10 |
| | | USB | 11 |
| | | Network | 12 |

## Requirements

- Home Assistant 2023.12.0 or newer
- Hegel H590 on the same network, reachable via TCP port 50001

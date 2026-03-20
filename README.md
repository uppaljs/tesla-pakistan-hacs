# Tesla Connect Pakistan — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![GitHub Release](https://img.shields.io/github/v/release/uppaljs/tesla-pakistan-hacs)](https://github.com/uppaljs/tesla-pakistan-hacs/releases)
[![License](https://img.shields.io/github/license/uppaljs/tesla-pakistan-hacs)](LICENSE)

Unofficial Home Assistant custom integration for **Tesla Industries Pakistan** smart geyser and inverter controllers.

> **Disclaimer:** This is an **unofficial**, community-built integration. The author has **no affiliation, relationship, or endorsement** from Tesla Industries Pakistan (https://tesla-pv.com). This project was created independently through reverse engineering of the Tesla Connect mobile application for personal home automation use. All product names, logos, and brands are property of their respective owners.

## Supported Devices

- **X-Gen Smart Water Geyser** — [Product page](https://tesla-pv.com/products/xgen-smart-water-geyser)
- **Tesla Inverters** — monitoring support

## Features

### Geyser
- **Water Heater entity** — set temperature, change mode (gas / electric / auto / solar), turn on/off (boost), away mode (vacation)
- **Sensors** — current temperature, target temperature, status, current mode, user mode, gas units, electric units
- **Switches** — boost, vacation mode, two-hour mode, 24 hourly timer slots
- **Binary sensors** — online status, burner active

### Inverter
- **Sensors** — battery percentage, battery voltage, energy (day/week/month/total), savings, faults
- **Binary sensors** — online status, grid status, solar status

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots menu → **Custom repositories**
4. Add `https://github.com/uppaljs/tesla-pakistan-hacs` and select **Integration** as the category
5. Search for **Tesla Connect Pakistan** and install
6. Restart Home Assistant

### Manual

1. Copy the `custom_components/tesla_connect_pakistan` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Tesla Connect Pakistan**
3. Enter your phone number (format: `03XXXXXXXXX`) and password (same as the Tesla Connect app)
4. Your devices will be automatically discovered and added

## Entities

For each **geyser** device:

| Entity | Type | Description |
|--------|------|-------------|
| Water heater | `water_heater` | Temperature + mode control, on/off (boost), away mode (vacation) |
| Current temperature | `sensor` | Current water temperature (°C) |
| Target temperature | `sensor` | Target temperature (°C) |
| Status | `sensor` | Status label from device |
| Current mode | `sensor` | Active operating mode |
| User mode | `sensor` | User-selected mode |
| Gas units | `sensor` | Gas consumption |
| Electric units | `sensor` | Electric consumption (Wh) |
| Boost | `switch` | Instant heat toggle |
| Vacation mode | `switch` | Vacation mode toggle |
| Two-hour mode | `switch` | Two-hour mode toggle |
| Timer 00:00–23:00 | `switch` × 24 | Hourly timer schedule slots |
| Online | `binary_sensor` | Device connectivity |
| Burner | `binary_sensor` | Burner active |

For each **inverter** device:

| Entity | Type | Description |
|--------|------|-------------|
| Battery | `sensor` | Battery percentage |
| Battery voltage | `sensor` | Battery voltage (V) |
| Energy today | `sensor` | Daily energy (Wh) |
| Energy this week | `sensor` | Weekly energy (Wh) |
| Energy this month | `sensor` | Monthly energy (Wh) |
| Energy total | `sensor` | Total energy (Wh) |
| Savings today | `sensor` | Daily savings |
| Faults | `sensor` | Fault code |
| Online | `binary_sensor` | Device connectivity |
| Grid | `binary_sensor` | Grid power status |
| Solar | `binary_sensor` | Solar power status |

## Water Heater Services

The geyser water heater entity supports all standard [Home Assistant water heater services](https://www.home-assistant.io/integrations/water_heater/):

| Service | Action |
|---------|--------|
| `water_heater.set_temperature` | Set target temperature (30–75 °C) |
| `water_heater.set_operation_mode` | Set mode: `gas`, `electric`, `auto`, `solar_on`, `solar_off` |
| `water_heater.turn_on` | Activate boost (immediate heating) |
| `water_heater.turn_off` | Deactivate boost |
| `water_heater.turn_away_mode_on` | Activate vacation mode |
| `water_heater.turn_away_mode_off` | Deactivate vacation mode |

## Technical Details

- **Polling interval:** 30 seconds
- **Token auto-refresh:** every 55 minutes
- **API:** Cloud polling via Tesla Connect API (`api.tesla-tech.com`)

## License

This project is provided as-is for personal use. Use at your own risk.

## Credits

- **Tesla Industries Pakistan** — manufacturer of the X-Gen Smart Water Geyser and inverters (https://tesla-pv.com)
- This integration was built by reverse engineering the [Tesla Connect](https://play.google.com/store/apps/details?id=com.tesla.connect) Android app

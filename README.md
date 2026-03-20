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
- **Sensors** — current temperature, target temperature, status, current mode, user mode, gas consumption (m³), electric consumption (kWh), schedule summary
- **Switches** — boost, vacation mode, two-hour mode, 24 hourly schedule slots (optional, can be disabled)
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

## Removal

1. Go to **Settings → Devices & Services**
2. Click on the **Tesla Connect Pakistan** integration card
3. Click the three dots menu → **Delete**
4. Restart Home Assistant
5. (Optional) Uninstall from HACS: **HACS → Integrations → Tesla Connect Pakistan → Uninstall**

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Tesla Connect Pakistan**
3. Enter your phone number (format: `03XXXXXXXXX`) and password (same as the Tesla Connect app)
4. Your devices will be automatically discovered and added

### Options

After setup, click **Configure** on the integration card to adjust:

| Option | Default | Range | Description |
|--------|---------|-------|-------------|
| Polling interval | 30 sec | 10–300 sec | How often to poll the API for device updates |
| Create hourly schedule switches | ON | — | Whether to create the 24 hourly timer switches |

Changing options automatically reloads the integration — no restart needed.

### Re-authentication

If your session expires or your password changes, Home Assistant will automatically prompt you to re-enter your credentials via the re-authentication flow.

### Reconfigure

To update your phone number or password on an existing entry, click the three dots menu on the integration card and select **Reconfigure**.

## Entities

For each **geyser** device:

| Entity | Type | Description |
|--------|------|-------------|
| Water heater | `water_heater` | Temperature + mode control, on/off (boost), away mode (vacation) |
| Current temperature | `sensor` | Current water temperature (°C) |
| Target temperature | `sensor` | Target temperature (°C) |
| Status | `sensor` | Status label from device |
| Current mode | `sensor` | What the geyser is actually running on (gas/electric/etc.) |
| User mode | `sensor` | What the user selected (may differ from current in auto mode) |
| Gas consumption | `sensor` | Cumulative gas usage (m³) |
| Electric consumption | `sensor` | Cumulative electric usage (kWh) |
| Schedule | `sensor` | Summary of active hours (e.g. "04:00–00:00") |
| Boost | `switch` | Instant heat toggle |
| Vacation mode | `switch` | Vacation mode toggle |
| Two-hour mode | `switch` | Two-hour mode toggle |
| Schedule 00:00–01:00 … 23:00–00:00 | `switch` × 24 | Hourly timer schedule slots (config category, optional) |
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
| `water_heater.set_operation_mode` | Set mode: `auto`, `electric`, `gas`, `solar_off`, `solar_on` |
| `water_heater.turn_on` | Activate boost (immediate heating) |
| `water_heater.turn_off` | Deactivate boost |
| `water_heater.turn_away_mode_on` | Activate vacation mode |
| `water_heater.turn_away_mode_off` | Deactivate vacation mode |

## Data Updates

This integration uses **cloud polling** to fetch device data from the Tesla Connect API (`api.tesla-tech.com`).

- **Polling interval:** configurable via Options (default 30 seconds, range 10–300s)
- **Token auto-refresh:** the session token is automatically refreshed every 55 minutes
- **Connection recovery:** if the API becomes unreachable, the integration logs once and retries automatically on each poll cycle; when the connection is restored, it logs once and resumes normal operation
- **Auth failure:** if credentials expire or become invalid, polling halts and HA automatically prompts you to re-authenticate

All entities update simultaneously via a shared `DataUpdateCoordinator`. No individual entity polling occurs.

## Supported Devices

| Device | Model | Support level |
|--------|-------|---------------|
| X-Gen Smart Water Geyser | type_id=2 | Full (monitoring + control) |
| Tesla Inverter | type_id=1 | Monitoring only |

Other Tesla Connect Pakistan devices may work if they appear in the login response, but only geyser and inverter types produce entities.

## Supported Functions

| Function | Platform | Geyser | Inverter |
|----------|----------|--------|----------|
| Temperature monitoring | sensor | Current + target temp | — |
| Energy tracking | sensor | Electric (kWh) + gas (m³) | Day/week/month/year/total (Wh) |
| Mode display | sensor | Current mode + user mode | — |
| Schedule display | sensor | Active hours summary | — |
| Battery monitoring | sensor | — | Percentage + voltage |
| Savings | sensor | — | Daily savings |
| Fault reporting | sensor | — | Fault code |
| Online status | binary_sensor | Connectivity | Connectivity |
| Burner active | binary_sensor | Heat state | — |
| Grid / Solar status | binary_sensor | — | Power source status |
| Boost toggle | switch | Instant heat on/off | — |
| Vacation mode | switch | Away mode on/off | — |
| Two-hour mode | switch | Timed heat on/off | — |
| Hourly schedule | switch × 24 | Per-hour on/off slots | — |
| Temperature control | water_heater | Set target 30–75 °C | — |
| Mode control | water_heater | gas/electric/auto/solar | — |
| On/Off (boost) | water_heater | Turn on = boost, off = normal | — |
| Away mode (vacation) | water_heater | Vacation mode toggle | — |

## Automation Examples

### Turn on boost when temperature drops below 40°C

```yaml
automation:
  - alias: "Geyser boost when cold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.221b_geyser_current_temperature
        below: 40
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.221b_geyser_boost
```

### Notify when geyser goes offline

```yaml
automation:
  - alias: "Geyser offline alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.221b_geyser_online
        to: "off"
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Geyser has been offline for 5 minutes"
```

### Set geyser to gas mode at night, auto during the day

```yaml
automation:
  - alias: "Geyser night gas mode"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: water_heater.set_operation_mode
        target:
          entity_id: water_heater.221b_geyser_water_heater
        data:
          operation_mode: gas

  - alias: "Geyser day auto mode"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: water_heater.set_operation_mode
        target:
          entity_id: water_heater.221b_geyser_water_heater
        data:
          operation_mode: auto
```

### Activate vacation mode when leaving home

```yaml
automation:
  - alias: "Geyser vacation when away"
    trigger:
      - platform: state
        entity_id: person.junaid
        to: "not_home"
        for: "01:00:00"
    action:
      - service: water_heater.turn_away_mode_on
        target:
          entity_id: water_heater.221b_geyser_water_heater
```

## Known Limitations

- **Cloud-only:** requires internet access to reach `api.tesla-tech.com`; no local/LAN control
- **No push notifications:** the integration polls the API; there is no real-time push from the device
- **Single account:** each integration instance supports one Tesla Connect account
- **Device list from login only:** the device list is only refreshed when the token expires and a re-login occurs (every ~55 minutes); new devices added via the mobile app may take up to an hour to appear
- **Inverter control:** inverter devices are monitoring-only; no control commands were found in the API
- **Timer schedule granularity:** the schedule operates in 1-hour blocks (24 slots); sub-hour scheduling is not supported by the API
- **No energy dashboard native support:** electric_units and gas_units are cumulative counters from the device; they may reset or behave unexpectedly depending on device firmware

## Troubleshooting

### Integration shows "Authentication failed"
Your phone number or password is incorrect, or the Tesla Connect account has been changed. Go to **Settings → Devices & Services → Tesla Connect Pakistan** and click **Reconfigure** to update your credentials.

### Entities show "Unavailable"
The Tesla Connect API may be temporarily unreachable. Check your internet connection. The integration will automatically recover when the API is available again. Check **Settings → System → Repairs → System information** for the server reachability status.

### Temperature or mode not updating
The integration polls every 30 seconds by default. If you need faster updates, go to the integration's **Configure** options and reduce the polling interval (minimum 10 seconds).

### Devices not appearing after adding in the mobile app
The device list is fetched during login. Force a refresh by going to **Settings → Devices & Services → Tesla Connect Pakistan → three dots → Reload**.

### Schedule switches not visible
Schedule switches are disabled by default in Options. Go to **Configure** on the integration card and enable "Create hourly schedule switches".

## Use Cases

- **Energy savings:** monitor gas and electric consumption over time, create automations to switch to the most efficient mode based on time of day
- **Comfort scheduling:** use the 24-hour timer schedule to heat water before you wake up and before you return home
- **Vacation mode:** automatically activate vacation mode when everyone leaves home using presence detection
- **Safety monitoring:** get alerts when the geyser goes offline or the burner stays active for unusually long periods
- **Solar optimization:** switch between solar and grid modes based on solar panel output from your inverter sensors
- **Dashboard:** build a Lovelace dashboard showing real-time geyser temperature, mode, and energy consumption alongside your inverter's battery and solar status

## Technical Details

- **HTTP fingerprint:** mimics the official Tesla Connect Android app (OkHttp UA, compact JSON, timestamp auth header)
- **External library:** all API communication handled by [pyteslaconnectpk](https://pypi.org/project/pyteslaconnectpk/) on PyPI

## Changelog

### v1.3.0
- **Diagnostics** — download redacted diagnostic data per config entry or per device (Settings → Integrations → Download diagnostics)
- **System health** — API reachability check, token validity, device count, authenticated user visible in Settings → System → Repairs → System information
- **Coordinator** — passes `config_entry` to `DataUpdateCoordinator` for proper HA lifecycle management; auth errors during polling now raise `ConfigEntryAuthFailed` (triggers reauth) instead of `UpdateFailed` (silent retry)
- **Setup failure handling** — fully documented `ConfigEntryAuthFailed` / `ConfigEntryNotReady` behaviour in `async_setup_entry`
- **Test suite** expanded to 54 tests (was 38)

### v1.2.0
- **Options flow** — configurable polling interval (10–300s) and toggle for schedule switches
- **Reauth flow** — automatic credential re-entry when session expires
- **Reconfigure flow** — update phone/password without deleting the entry
- **Electric units** now displayed in kWh (was raw watts)
- **Gas units** now displayed in m³ with proper HA gas device class
- **Schedule summary sensor** — shows active ranges like "04:00–00:00"
- **Schedule switches** moved to config category, renamed "Schedule HH:00–HH:00"
- **Mode sensors** — friendly labels, distinct icons, clear curr_mode vs user_mode
- **Brand assets** added for HACS logo display
- **HA coding style** — full PEP 257/PEP 8 compliance, Google-style docstrings
- **Test suite** — 38 tests covering API, config flow, sensors, switches, water heater
- **Error handling** — `ConfigEntryAuthFailed` for auth errors, `ConfigEntryNotReady` for connection errors
- **manifest.json** — `integration_type: hub`, `loggers` field added

### v1.0.0
- Initial release
- Water heater, sensors, switches, binary sensors for geyser and inverter
- Automatic device discovery on login
- HACS compatible

## License

This project is provided as-is for personal use. Use at your own risk.

## Credits

- **Tesla Industries Pakistan** — manufacturer of the X-Gen Smart Water Geyser and inverters (https://tesla-pv.com)
- This integration was built by reverse engineering the [Tesla Connect](https://play.google.com/store/apps/details?id=com.tesla.connect) Android app

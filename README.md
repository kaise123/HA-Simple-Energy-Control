# Simple HA Energy Control

An automated energy management package for Home Assistant. This project controls an AlphaESS battery system using live and forecasted wholesale electricity prices from Amber Electric. It uses multi-tier State of Charge (SOC) rules, predictive 12-hour forecasting, and Modbus dispatch controls to optimise battery charging during low-price periods and grid exporting during high-price events.

This can easily be adapted to work with other battery systems and energy providers — but in this state is set up for AlphaESS and Amber Electric.

## Features

* **Multi-Tier Export and Import Rules:** Define price thresholds that adjust dynamically based on current battery capacity. For example, configure the system to export at $0.20/kWh when SOC is >80%, but require $1.00/kWh when SOC is <30%.
* **Optimised Grid Charging:** When import prices drop below your threshold, the system activates AlphaESS **Optimise Consumption (Mode 6)** — which force-charges the battery at full power from the grid while PV output also contributes.
* **Predictive Holds:** Evaluates the next 12 hours of Amber price forecasts. If a significant price event is anticipated, the system can temporarily suspend standard rules to preserve battery capacity for higher returns or lower charging costs.
* **Hysteresis Logic:** Applies a configurable buffer to target prices to prevent the inverter from rapidly toggling between states when live prices fluctuate around a threshold.
* **State-Based Notifications:** Triggers mobile push notifications only when the active dispatch tier changes, reducing alert fatigue.
* **Custom Lovelace Dashboard:** Provides a consolidated interface for status tracking, live power flows, price trend graphs, rule configuration, and manual Modbus overrides.

---

## Prerequisites

Before installing, ensure the following integrations and frontend components are already installed and configured:

### Integrations

1. **[Amber Electric](https://github.com/hass-energy/amber-express)**: Configured with your API key. Provides:
   - `sensor.amber_express_home_general_price`
   - `sensor.amber_express_home_feed_in_price`

2. **[AlphaESS Modbus (hillviewlodge.ie/alphaess)](https://projects.hillviewlodge.ie/alphaess/)**: AlphaESS inverter configured for local Modbus TCP control. Provides the helper entities used to trigger dispatch modes. Specifically required:
   - `input_select.alphaess_helper_dispatch_mode`
   - `input_number.alphaess_helper_dispatch_duration`
   - `input_boolean.alphaess_helper_dispatch`
   - `input_button.alphaess_helper_dispatch_reset_full`
   - `sensor.alphaess_soc_battery`

3. **Home Energy Monitor**: Any sensor reporting site consumption in watts (e.g. a Shelly EM).

4. **Mobile App**: A `notify.mobile_app_phone` notification service. Replace this with your actual device name if it differs.

### Frontend Cards (HACS)

The dashboard requires these custom Lovelace cards:
* [`power-flow-card-plus`](https://github.com/flixlix/power-flow-card-plus)
* [`apexcharts-card`](https://github.com/RomRider/apexcharts-card)

---

## Installation

Simple HA Energy Control is distributed as a native **Home Assistant Package** — a single YAML file that is automatically loaded by HA alongside your main configuration. No custom integrations or Python code required.

### 1. Enable HA Packages (once only)

If you haven't already, add the following to your `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

This tells Home Assistant to automatically load any `.yaml` file placed in the `packages/` folder inside your HA config directory.

> **Already using packages?** If you already have a `packages:` block, just ensure the `packages/` folder is included. You can also use a named include to avoid conflicts:
> ```yaml
> homeassistant:
>   packages:
>     simple_ha_energy_control: !include packages/simple_ha_energy_control.yaml
> ```

### 2. Copy the Package File

Copy [`packages/simple_ha_energy_control.yaml`](packages/simple_ha_energy_control.yaml) from this repository into the `packages/` folder in your Home Assistant config directory.

### 3. Update Entity IDs (if required)

If any of your Amber or notification entity IDs differ from the defaults, find-and-replace the following in `simple_ha_energy_control.yaml` before copying:

| Default entity | Replace with |
|---|---|
| `sensor.amber_express_home_general_price` | Your Amber import price sensor |
| `sensor.amber_express_home_feed_in_price` | Your Amber feed-in price sensor |
| `notify.mobile_app_phone` | Your mobile notification service |

### 4. Restart Home Assistant

Go to **Settings → System → Restart**. After restarting, all helpers, template sensors, and the automation will be active.

### 5. Configure the Dashboard (manual)

1. Create a new View in your Home Assistant Dashboard.
2. Enter Edit mode (pencil icon) → options menu (⋮) → **Raw Configuration Editor**.
3. Paste the contents of [`dashboard.yaml`](dashboard.yaml) into the new view block.
4. Click **Save**.

---

## Usage Guide

### Setting Tiers

The automation evaluates rules in descending priority from Tier 1 to Tier 3.

* **Exporting:** When feed-in price and SOC conditions are met, the automation activates **Maximise Output (Mode 4)** for 30 minutes, discharging the battery to the grid at maximum power.
* **Importing:** When import prices drop below your threshold, the automation activates **Optimise Consumption (Mode 6)** for 30 minutes. The battery force-charges at full power from the grid while PV output also contributes.

### Predictive Holds

When enabled, the system evaluates the `forecasts` attribute of the Amber price sensors 12 hours ahead. For example, if a Tier 1 rule is set to export at $0.30/kWh, but the forecast shows a $1.50/kWh peak later in the day, the system can block the immediate export to preserve battery capacity — provided the forecasted peak exceeds your configured predictive threshold.

### Manual Overrides

The Master Automation Switch disables all automation logic. Manual controls at the bottom of the dashboard can then be used to select specific dispatch modes directly. Clicking **Reset to Normal Mode** returns the inverter to standard self-consumption.

---

## Dispatch Modes Reference

| Mode | Label | Behaviour |
|---|---|---|
| 4 | Maximise Output | Forces battery discharge; maximises power exported to the grid |
| 5 | Normal | Standard self-consumption (the reset target) |
| 6 | Optimise Consumption | Force-charges battery at full power from the grid; PV also contributes |

---

## File Structure

```
HA-Simple-Energy-Control/
├── packages/
│   └── simple_ha_energy_control.yaml   # ★ Install this into your HA packages/ folder
├── dashboard.yaml                       # Lovelace dashboard (paste into a new view)
├── automations.yaml                     # Legacy reference only
├── configuration.yaml                   # Legacy reference only
└── README.md
```

---

## License

[MIT](LICENSE)

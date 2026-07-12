# Home Assistant Simple Energy Control

An automated energy management configuration for Home Assistant. This project controls an AlphaESS battery system using live and forecasted wholesale electricity prices from Amber Electric. It uses multi-tier State of Charge (SOC) rules, predictive 12-hour forecasting, and Modbus dispatch controls to optimize battery charging during low-price periods and grid exporting during high-price events.

This can easily be adapted to work with other battery systems and energy providers - but in this state is set up for AlphaESS and Amber Electric.

## Features

* **Multi-Tier Export and Import Rules:** Define price thresholds that adjust dynamically based on current battery capacity. For example, you can configure the system to export at $0.20/kWh when SOC is >80%, but require $1.00/kWh when SOC is <30%.
* **Predictive Holds:** Evaluates the next 12 hours of Amber price forecasts. If a significant price event is anticipated, the system can temporarily suspend standard rules to preserve battery capacity for higher returns or lower charging costs.
* **Hysteresis Logic:** Applies a configurable buffer to target prices to prevent the inverter from rapidly toggling between states when live prices fluctuate around a threshold.
* **State-Based Notifications:** Triggers mobile push notifications only when the active dispatch tier changes, reducing alert fatigue.
* **Custom Lovelace Dashboard:** Provides a consolidated interface for status tracking, live power flows, price trend graphs, rule configuration, and manual Modbus overrides.

---

## Prerequisites

Before implementing this configuration, ensure the following integrations and frontend components are installed and configured in your Home Assistant instance:

### Integrations
1. **[Amber Express](https://github.com/hass-energy/amber-express)**: Amber Express integration configured with your API key.
2. **AlphaESS Modbus**: The AlphaESS inverter must be configured for local Modbus control. This automation relies on the specific `input_select`, `input_number`, and `input_boolean` helper entities used to trigger AlphaESS dispatch modes. Specifically, I have used https://projects.hillviewlodge.ie/alphaess/ to integrate AlphaESS with Home Assistant using Modbus.
3. **Home Energy Monitor**: A sensor monitoring total site consumption (this project uses a Shelly EM as an example - but any sensor reporting watts will do).

### Frontend Cards (HACS)
The dashboard requires the following custom cards, available via the Home Assistant Community Store (HACS):
* [`power-flow-card-plus`](https://github.com/flixlix/power-flow-card-plus)
* [`apexcharts-card`](https://github.com/RomRider/apexcharts-card)

---

## Installation

### 1. Update Entity IDs
Before copying the configuration files, execute a find-and-replace to map the template entity IDs to your specific Home Assistant environment. 

Key entities to update:
* `sensor.amber_express_home_general_price` -> Replace with your Amber General/Import price sensor.
* `sensor.amber_express_home_feed_in_price` -> Replace with your Amber Feed-in/Export price sensor.
* `sensor.shelly_ct1_power` -> Replace with your home consumption sensor.
* `notify.mobile_app_phone` -> Replace with your specific mobile app notification service.

### 2. Configuration Helpers (`configuration.yaml`)
The automation relies on several helper entities (Input Booleans, Input Numbers, Input Texts) and Template Sensors. 

Copy the relevant sections from `configuration.yaml` in this repository into your own. Alternatively, these can be created manually via the UI (Settings > Devices & Services > Helpers). Note that `input_number` helpers should be configured with `mode: box` to display as text-entry fields on the dashboard.

### 3. Automation Logic (`automations.yaml`)
Copy the contents of `automations.yaml` into your Home Assistant automations file. This script triggers on changes to the battery SOC or Amber prices, evaluates the tiered rules and predictive holds, applies the hysteresis offset, and issues the appropriate Modbus dispatch command.

### 4. Lovelace Dashboard
1. Create a new View in your Home Assistant Dashboard.
2. Enter Edit mode (pencil icon), select the options menu (three dots), and open the **Raw Configuration Editor**.
3. Paste the contents of `dashboard.yaml` into the new view block.

---

## Usage Guide

Once installed, use the Energy Management dashboard to configure the system's behavior.

### Setting Tiers
The automation evaluates rules in descending order from Tier 1 to Tier 3. 
* **Exporting:** When price and SOC conditions are met, the automation sets the AlphaESS to 'Maximise Output' (Mode 4) for 30 minutes.
* **Importing:** When prices drop below the target threshold, it sets the AlphaESS to 'State of Charge Control' (Mode 2) to force-charge the battery.

### Predictive Holds
When enabled, the system evaluates the `forecasts` attribute of the Amber sensors. For example, if a Tier 1 rule is configured to export at $0.30/kWh, but the forecast indicates a peak of $1.50/kWh later in the day, the system can block the immediate export to preserve capacity, provided the forecasted peak exceeds your configured predictive threshold.

### Manual Overrides
The Master Automation Switch disables the script entirely. Manual controls at the bottom of the dashboard can then be used to dictate specific Modbus dispatch modes. Clicking "Reset to Normal Mode" clears all overrides and returns the inverter to standard self-consumption (Mode 5).

---

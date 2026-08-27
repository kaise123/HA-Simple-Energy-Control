# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.2.2] - 2026-08-27

### Fixed
- **60-Minute Timeout Reset Bug**: Fixed an issue where the 60-minute hardware dispatch timer failed to renew seamlessly. The keep-alive routine now actively monitors `timer.alphaess_helper_dispatch_timer` and oscillates `input_number.alphaess_helper_dispatch_duration` (between 60 and 59) to force Modbus state updates without dropping the active dispatch session.

## [1.2.1] - 2026-08-26

### Fixed
- **Continuous Dispatch Expiry Bug**: Fixed an issue where export/import operations running longer than 60 minutes stopped when the hardware duration timer expired because steady-state runs skipped re-dispatching.
- **Rate-Limited Keep-Alive Refresh**: Added a 45-minute keep-alive renewal and dispatch-off timeout trigger that refreshes active dispatch sessions seamlessly without sending redundant Modbus writes during regular price and SOC ticks.
- **Datetime Exception Risk**: Fixed a Jinja template vulnerability in the Keep-Alive block by replacing `default(0)` with `as_timestamp(0)` on `last_changed` attributes, preventing hard crashes during Home Assistant startup.
- **Missing State-Change Notifications**: Resolved a bug where rapid state shifts (e.g. going from 'Idle' directly to 'Solar Curtailed') failed to trigger mobile push notifications due to deeply nested logic traps.

### Changed
- **Unified Notification Manager**: Completely decoupled push notifications from Modbus dispatch blocks. The automation now evaluates state changes at the very beginning of the run and triggers a single, deduplicated, context-rich push notification mapping 1:1 with the active logic choice.
- **Dashboard Layout Polish**: Restructured the "Predictive Solar Soak & Curtailment" and "Predictive Battery Hold" cards in `dashboard.yaml` to match the clean, readable format of the "Export Tiers" card.

---

## [1.2.0] - 2026-08-21

### Added
- **Predictive Solar Soaking (`input_boolean.amber_solar_soak_enabled`)**: Automatically pre-discharges the battery during the morning positive feed-in price window down to a calculated target SOC when Solcast forecasts excess solar generation during an upcoming negative price dip.
- **Negative Price Curtailment (`input_boolean.amber_curtailment_enabled`)**: Automatically halts all export dispatch modes and resets the inverter to Normal Mode (Mode 5 / self-consumption) when feed-in prices drop below `input_number.amber_curtailment_price_threshold` (default: $0.00/kWh).
- **Solcast 10% Forecast Template Sensor (`sensor.amber_solcast_10_forecast`)**: Resiliently extracts conservative 10th percentile solar generation estimates (kWh) from Solcast via `estimate10`, `pv_estimate10`, or `detailedForecast` attributes.
- **Negative Export 12h Template Sensor (`sensor.amber_negative_export_forecast_12h`)**: Analyzes the upcoming 12 hours of Amber Express feed-in forecasts to detect upcoming negative price intervals.
- **Solar Soak Target SOC Sensor (`sensor.amber_solar_soak_target_soc`)**: Calculates the optimal battery headroom percentage required to absorb expected excess midday solar.
- **Dedicated Solar Soak Minimum SOC Floor (`input_number.amber_soak_min_soc`)**: Configurable floor to prevent solar soak pre-exporting from discharging the battery below a user-defined reserve (default: 20%), independent of the emergency export SOC guard.
- **Configurable Soak Parameters**:
  - `input_number.amber_battery_capacity`: Total battery capacity (kWh).
  - `input_number.amber_soak_max_target_soc`: Maximum SOC ceiling for solar charging (default: 95%).
  - `input_number.amber_soak_forecast_weight`: Multiplier to scale Solcast estimates up or down (range: 0.20–2.00, default: 1.00).
  - `input_number.amber_soak_min_pre_export_price`: Minimum positive feed-in price required before discharging for solar soak (default: $0.05/kWh).
  - `input_number.amber_curtailment_price_threshold`: Feed-in price below which curtailment engages (default: $0.00/kWh).
- **Dashboard Solar Soak & Curtailment Control Card**: New interactive card in `dashboard.yaml` displaying live Solcast 10% forecast, target soak SOC, negative pricing alerts, and full slider tuning controls.
- **Solar Soak & Curtailment Push Notifications**: Distinct mobile notifications when pre-exporting or negative-price curtailment triggers.

### Changed
- **Automation State Machine**: Updated priority sequence to evaluate curtailment, predictive holds, solar soak pre-exporting, and standard tiers in strict hierarchical order.
- **Export Trigger**: Updated to support both standard export tiers (checked against `amber_export_min_soc_guard`) and solar soak pre-exporting (checked against `amber_soak_min_soc`).
- **Trigger List**: Expanded to react dynamically to Solcast updates, negative price forecasts, and all new Solar Soak / Curtailment tuning helpers.

---

## [1.1.1] - 2026-08-14

### Fixed
- **Status evaluation bug**: resolved an issue where Jinja whitespace formatting caused the automation to silently fail and fall back to Normal Mode when attempting to activate export or import tiers.
- **Export SOC guard status**: the dashboard status now correctly shows when an export is blocked by the minimum SOC guard, instead of incorrectly displaying an active export state.

---

## [1.1.0] - 2026-08-12

### Added
- **Export Minimum SOC Guard** (`input_number.amber_export_min_soc_guard`): configurable hard floor on battery SOC below which exporting is always blocked, regardless of tier rules. Previously hardcoded to 10 %. Now adjustable from the Advanced Tuning dashboard tab.
- **Comprehensive automation triggers**: all tier enable/disable booleans and all price/SOC threshold `input_number` entities are now included in the trigger list, so rule changes take effect immediately without waiting for the next price tick.
- **`time_pattern` safety trigger** (every 30 minutes): ensures the automation re-evaluates even during price-quiet periods and that the dispatch duration failsafe never silently drifts.
- **`state_class: measurement`** on both template sensors (`amber_max_export_forecast_12h`, `amber_min_import_forecast_12h`): enables long-term statistics recording and Energy Dashboard compatibility.
- **Dispatch Duration** entity now visible in the Manual Controls dashboard card.
- **Export SOC Guard** section added to the Advanced Tuning dashboard tab.
- **Dispatch Duration and Failsafe** section added to README Usage Guide.
- **Corrected dashboard installation instructions** in README (Option A: new dashboard; Option B: append views to existing dashboard).

### Changed
- **`mode: restart`** (was `mode: single`): the automation now restarts on new triggers rather than silently dropping them, ensuring the most recent price data is always used.
- **Dispatch duration reduced from 180 → 60 minutes**: 60 minutes is a true failsafe; under normal operation the automation resets the inverter on the next price tick. The 30-minute `time_pattern` trigger provides an additional safety net.
- **`active_action` predictive hold logic corrected**: holds now activate unconditionally when a predictive condition is true. Previously a spurious secondary price-threshold check caused the status to show `Idle` while a hold was silently active.
- **`new_status_text` driven entirely from `active_action`**: eliminates any possible divergence between the displayed status and the action actually taken.
- **`pred_exp_active` / `pred_imp_active`** now call `states('sensor...')` directly instead of referencing same-block Jinja variables, making evaluation order explicit.
- **Forecast template sensors** now use an `as_datetime()` loop for time-window filtering instead of lexicographic ISO string comparison — correctly handles mixed timezone formats in the Amber Express forecast attribute.
- **`not_to: ['unknown', 'unavailable']`** added to price and SOC sensor triggers: prevents spurious dispatch commands on HA startup or sensor outages.
- **Dashboard CRLF line endings normalised** to LF throughout `dashboard.yaml`.
- **Dashboard predictive hold card**: all `|float` calls now include safe defaults to prevent template errors when sensors are unavailable.
- **Mode 2 description corrected** — no longer incorrectly described as used by the automation for cheap imports.
- **Mode 6 description corrected** — clarified as grid-first force-charge; marked as the mode used by the automation for cheap imports.
- **README**: removed incorrect "for 30 minutes" dispatch duration claim from export and import tier descriptions.

### Fixed
- Automation disabled early-exit comment cleaned up (previously referenced an internal "Issue 3 fix" note).
- "Up to 3 hours" wording in export/import trigger comments corrected to "up to 60 minutes".

---

## [1.0.0] - 2026-08-11

### Added
- Initial release.
- Multi-tier export and import rules with configurable SOC and price thresholds.
- Predictive 12-hour hold logic using Amber Express forecast attributes.
- Asymmetric hysteresis (immediate entry, buffered exit) for price and SOC.
- AlphaESS Modbus dispatch via hillviewlodge.ie integration helpers.
- Mobile push notifications on tier changes.
- Custom Lovelace dashboard (power flow, price trends, rule config, manual overrides).
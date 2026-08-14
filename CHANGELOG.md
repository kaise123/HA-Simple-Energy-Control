# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
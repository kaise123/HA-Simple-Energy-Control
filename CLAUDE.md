# HA Simple Energy Control

A Home Assistant package that optimises an AlphaESS battery using Amber Express prices and Solcast forecasts. See `README.md` for features and install steps.

## Layout
- `packages/ha_simple_energy_control.yaml` — helpers, template sensors, automations (the engine).
- `dashboard.yaml` — production Lovelace dashboard.
- `debug_dashboard.yaml` — diagnostics, tuneables, simulation tools.
- `CHANGELOG.md` — Keep a Changelog format; add entries under `[Unreleased]`.
- `LocalOnly/` — git-ignored copies with the live site's entity names. Never commit.
- AlphaESS dispatch modes: 4 Maximise Output, 5 Normal, 6 Optimise Consumption, 7 Maximise Consumption.

## Workflow
- Load the `home-assistant-best-practices` skill before editing HA YAML.
- For new features, non-trivial fixes or refactors, use plan mode before editing. The plan covers: problem and root cause, solution architecture, implementation steps across package and dashboards, and verification. Use Mermaid (`flowchart`, `stateDiagram-v2`) for control flow, priority trees and fallback logic. Wait for approval before editing.
- The live HA instance is reachable via the `home-assistant` MCP server. It may be running older code than the repo (at last check the package was not deployed), so verify against live state rather than assuming.
- After YAML changes, validate with `ha_get_system_health(include="config_check")`. Do not restart HA, deploy automations, or write to the instance over MCP without asking first.
- After changes, summarise what changed in: the package, `dashboard.yaml`, `debug_dashboard.yaml`, `LocalOnly/` and `CHANGELOG.md`.

## Dashboard parity
- Any automation, script, template or integration change that adds or alters user-facing entities must update the relevant view in `dashboard.yaml` in the same change. No new toggles, scenes or states without UI cards.
- Remove deprecated or renamed entities from every view to avoid "entity not found" cards.

## Debug dashboard
- Every new entity, diagnostic attribute, helper (`input_boolean`, `input_number`, `input_select`, `timer`) or intermediate sensor must be exposed in `debug_dashboard.yaml`.
- Every new threshold, timeout or setpoint needs an interactive control (slider, selector or toggle) there.
- Show raw state, last-triggered time and calculation attributes for new automations. Group entities by pipeline using `entities` or `grid` cards.

## LocalOnly mirrors
After changing `dashboard.yaml`, `debug_dashboard.yaml` or the package, run:

```powershell
pwsh scripts/sync_localonly.ps1
```

- It copies the files into `LocalOnly/` and substitutes `_home_` → `_home_` and `_phone` → `_phone`.
- Do not read or open `LocalOnly/` files; run the script instead. They are denied in `.claude/settings.json` to keep them out of context.

## Git
- Conventional commits (`feat:`, `fix:`, `chore:`, `docs:`), matching existing history.
- Only commit or push when asked. Never force-push.
- Files use CRLF locally (`core.autocrlf=true`); don't churn line endings.

import re

with open('packages/ha_simple_energy_control.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Negative Export Forecast cutoff and hysteresis
old_cutoff = '''            {# Dynamic cutoff: use first negative price if found, else default to daytime solar ramp ~10:30 #}
            {% set default_cutoff = today_at("10:30") if now() < today_at("10:30") else now() %}
            {% set cutoff = ns.t_neg if ns.t_neg is not none and ns.t_neg < today_at("16:00") else default_cutoff %}'''
new_cutoff = '''            {# Dynamic cutoff: use first negative price if found, else default to daytime solar ramp ~10:30 #}
            {% set today_1030 = today_at("10:30") %}
            {% set default_cutoff = today_1030 if now() < today_1030 else (today_1030 + timedelta(days=1)) %}
            {% set max_cutoff = today_at("16:00") if now() < today_at("16:00") else (today_at("16:00") + timedelta(days=1)) %}
            {% set cutoff = ns.t_neg if ns.t_neg is not none and ns.t_neg < max_cutoff else default_cutoff %}'''
content = content.replace(old_cutoff, new_cutoff)

old_soak_latch = '''              {% if currently_soaking %}
                {% set live_price = states('sensor.amber_express_home_feed_in_price') | float(0) %}
                {{ 'on' if live_price >= min_export_price else 'off' }}'''
new_soak_latch = '''              {% if currently_soaking %}
                {% set live_price = (states('sensor.amber_express_home_feed_in_price') | float(0)) * 100 %}
                {% set price_hysteresis = states('input_number.amber_price_hysteresis') | float(0) %}
                {{ 'on' if live_price >= (min_export_price - price_hysteresis) else 'off' }}'''
content = content.replace(old_soak_latch, new_soak_latch)

old_best_avg = '''                        {% set w_ns.sum = w_ns.sum + (w_item.value | float(0)) %}'''
new_best_avg = '''                        {% set w_ns.sum = w_ns.sum + ((w_item.value | float(0)) * 100) %}'''
content = content.replace(old_best_avg, new_best_avg)

# 2. Update Target SOC recalculation to 16:00
old_trigger = '''      - platform: time
        at: "00:01:00"
      - platform: time
        at: "06:00:00"
      - platform: homeassistant'''
new_trigger = '''      - platform: time
        at: "00:01:00"
      - platform: time
        at: "06:00:00"
      - platform: time
        at: "16:00:00"
      - platform: homeassistant'''
content = content.replace(old_trigger, new_trigger)

# 3. Solar Soak reset at 16:00 instead of 00:00
old_reset = '''      - platform: time
        at: "00:00:00"
        id: "midnight_reset"'''
new_reset = '''      - platform: time
        at: "16:00:00"
        id: "midnight_reset"'''
content = content.replace(old_reset, new_reset)

# 4. Input Numbers (Dollar to Cents)
replacements = {
    'min: -5\n    max: 20\n    step: 0.01\n    mode: box\n    unit_of_measurement: "$/kWh"': 'min: -500\n    max: 2000\n    step: 1\n    mode: box\n    unit_of_measurement: "c/kWh"',
    'min: 0\n    max: 1\n    step: 0.01\n    mode: box\n    unit_of_measurement: "$/kWh"': 'min: 0\n    max: 100\n    step: 1\n    mode: box\n    unit_of_measurement: "c/kWh"',
    'min: 0\n    max: 20\n    step: 0.01\n    mode: box\n    unit_of_measurement: "$/kWh"': 'min: 0\n    max: 2000\n    step: 1\n    mode: box\n    unit_of_measurement: "c/kWh"',
    'min: 0.00\n    max: 1.00\n    step: 0.01\n    mode: box\n    unit_of_measurement: "$/kWh"': 'min: 0\n    max: 100\n    step: 1\n    mode: box\n    unit_of_measurement: "c/kWh"',
    'min: -2.00\n    max: 0.50\n    step: 0.01\n    mode: box\n    unit_of_measurement: "$/kWh"': 'min: -200\n    max: 50\n    step: 1\n    mode: box\n    unit_of_measurement: "c/kWh"',
}
for k, v in replacements.items():
    content = content.replace(k, v)

# 5. Active variables
old_vars = '''          soc: "{{ states('sensor.alphaess_soc_battery') | float(0) }}"
          import_price: "{{ states('sensor.amber_express_home_general_price') | float(0) }}"
          export_price: "{{ states('sensor.amber_express_home_feed_in_price') | float(0) }}"'''
new_vars = '''          soc: "{{ states('sensor.alphaess_soc_battery') | float(0) }}"
          import_price: "{{ (states('sensor.amber_express_home_general_price') | float(0)) * 100 }}"
          export_price: "{{ (states('sensor.amber_express_home_feed_in_price') | float(0)) * 100 }}"'''
content = content.replace(old_vars, new_vars)

# 6. Curtailment logic (remove full battery check)
old_curtail = '''          curtailment_active: >
            {{ is_state('input_boolean.amber_curtailment_enabled', 'on')
               and is_state('sensor.alphaess_battery_full', 'true')
               and ('''
new_curtail = '''          curtailment_active: >
            {{ is_state('input_boolean.amber_curtailment_enabled', 'on')
               and ('''
content = content.replace(old_curtail, new_curtail)

# 7. Tier Export Forecasted (Gate it by predictive toggle!)
old_tier_exp = '''          tier_export_forecasted: >
            {% set active_tiers = [
              states('input_number.amber_export_price_1')|float(999) if is_state('input_boolean.amber_export_tier_1_enabled', 'on') else 999,
              states('input_number.amber_export_price_2')|float(999) if is_state('input_boolean.amber_export_tier_2_enabled', 'on') else 999,
              states('input_number.amber_export_price_3')|float(999) if is_state('input_boolean.amber_export_tier_3_enabled', 'on') else 999
            ] %}
            {% set min_tier = active_tiers | min %}
            {{ min_tier < 990 and states('sensor.amber_max_export_forecast_12h')|float(0) >= min_tier }}'''
new_tier_exp = '''          tier_export_forecasted: >
            {% set active_tiers = [
              states('input_number.amber_export_price_1')|float(9999) if is_state('input_boolean.amber_export_tier_1_enabled', 'on') else 9999,
              states('input_number.amber_export_price_2')|float(9999) if is_state('input_boolean.amber_export_tier_2_enabled', 'on') else 9999,
              states('input_number.amber_export_price_3')|float(9999) if is_state('input_boolean.amber_export_tier_3_enabled', 'on') else 9999
            ] %}
            {% set min_tier = active_tiers | min %}
            {{ is_state('input_boolean.amber_predictive_export_hold', 'on') and min_tier < 9990 and states('sensor.amber_max_export_forecast_12h')|float(0) >= min_tier }}'''
content = content.replace(old_tier_exp, new_tier_exp)

# 8. Soak priority vs holding priority
old_action = '''            {%- if not enabled -%} disabled
            {%- elif curtailment_active -%} curtailed
            {%- elif pred_exp_active or (tier_export_forecasted and not (t1_exp or t2_exp or t3_exp)) -%} holding_export
            {%- elif pred_imp_active -%} holding_import
            {%- elif soak_exp_active -%} solar_soak'''
new_action = '''            {%- if not enabled -%} disabled
            {%- elif curtailment_active -%} curtailed
            {%- elif soak_exp_active -%} solar_soak
            {%- elif pred_exp_active or (tier_export_forecasted and not (t1_exp or t2_exp or t3_exp)) -%} holding_export
            {%- elif pred_imp_active -%} holding_import'''
content = content.replace(old_action, new_action)

# Add soak min price hysteresis
old_soak_act = '''               and export_price >= states('input_number.amber_soak_min_pre_export_price')|float(0.00)'''
new_soak_act = '''               and export_price >= (states('input_number.amber_soak_min_pre_export_price')|float(0.00) - (hysteresis if currently_soaking else 0))'''
content = content.replace(old_soak_act, new_soak_act)


# 9. Actions - Curtailment implementation
old_choose_start = '''      - choose:
          # --- EXPORT / SOLAR SOAK TRIGGER ---'''
new_choose_start = '''      - choose:
          # --- CURTAILMENT TRIGGER ---
          - conditions:
              - condition: template
                value_template: "{{ active_action == 'curtailed' }}"
            sequence:
              - if:
                  - condition: template
                    value_template: "{{ current_status != new_status_text }}"
                then:
                  - service: input_number.set_value
                    target:
                      entity_id: input_number.alphaess_helper_max_feed_to_grid
                    data:
                      value: 0

          # --- EXPORT / SOLAR SOAK TRIGGER ---'''
content = content.replace(old_choose_start, new_choose_start)

old_default = '''        default:
          - if:
              - condition: template
                value_template: >
                  {{ current_status != new_status_text and
                     ('Exporting' in current_status or 'Importing' in current_status or 'Solar Soak' in current_status) }}
            then:
              - service: input_boolean.turn_off'''
new_default = '''        default:
          - if:
              - condition: template
                value_template: >
                  {{ current_status != new_status_text and
                     ('Exporting' in current_status or 'Importing' in current_status or 'Solar Soak' in current_status or 'Solar Curtailed' in current_status) }}
            then:
              - service: input_number.set_value
                target:
                  entity_id: input_number.alphaess_helper_max_feed_to_grid
                data:
                  value: 100
              - service: input_boolean.turn_off'''
content = content.replace(old_default, new_default)

# 10. Fix display format for notifications (c/kWh)
old_notify = '''                  Pre-exporting battery from {{ soc | int(0) }}% down to {{ soak_target_soc | int(20) }}% Target SoC to absorb upcoming midday solar. Feed-in: ${{ export_price }}/kWh.
                {% elif active_action == 'idle' %}
                  Prices have normalised. Returning to standard self-consumption.
                {% elif active_action == 'curtailed' %}
                  Feed-in price is ${{ export_price }}/kWh. Halting exports to protect against negative tariffs.
                {% elif active_action == 'disabled' %}
                  The master switch has been turned off. Returning to manual control.
                {% elif 'export' in active_action %}
                  {{ new_status_text }} - Feed-in is ${{ export_price }}/kWh (SOC: {{ soc }}%).
                {% elif 'import' in active_action %}
                  {{ new_status_text }} - Import is ${{ import_price }}/kWh (SOC: {{ soc }}%).
                {% else %}
                  {{ new_status_text }} (Feed-in: ${{ export_price }}/kWh, Import: ${{ import_price }}/kWh, SOC: {{ soc }}%).'''
new_notify = '''                  Pre-exporting battery from {{ soc | int(0) }}% down to {{ soak_target_soc | int(20) }}% Target SoC to absorb upcoming midday solar. Feed-in: {{ export_price | round(1) }}c/kWh.
                {% elif active_action == 'idle' %}
                  Prices have normalised. Returning to standard self-consumption.
                {% elif active_action == 'curtailed' %}
                  Feed-in price is {{ export_price | round(1) }}c/kWh. Halting exports to protect against negative tariffs.
                {% elif active_action == 'disabled' %}
                  The master switch has been turned off. Returning to manual control.
                {% elif 'export' in active_action %}
                  {{ new_status_text }} - Feed-in is {{ export_price | round(1) }}c/kWh (SOC: {{ soc }}%).
                {% elif 'import' in active_action %}
                  {{ new_status_text }} - Import is {{ import_price | round(1) }}c/kWh (SOC: {{ soc }}%).
                {% else %}
                  {{ new_status_text }} (Feed-in: {{ export_price | round(1) }}c/kWh, Import: {{ import_price | round(1) }}c/kWh, SOC: {{ soc }}%).'''
content = content.replace(old_notify, new_notify)

with open('packages/ha_simple_energy_control.yaml', 'w', encoding='utf-8') as f:
    f.write(content)

print("Python script executed.")

import re

dashboard = r"c:\Users\Administrator\Github\HA-Simple-Energy-Control\debug_dashboard.yaml"

with open(dashboard, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove tier_export_forecasted definitions
content = re.sub(
    r"              {% set active_tiers = \[\n.*?\n.*?\n.*?\n              \] %}\n              {% set min_tier = active_tiers \| min %}\n              {% set tier_export_forecasted = min_tier < 990 and max_exp_12h >= min_tier %}\n",
    "",
    content,
    flags=re.MULTILINE
)

# 2. Remove tier_export_forecasted from soak_exp_active
content = content.replace("and not tier_export_forecasted ", "")
content = content.replace(", Future Spike: {{ 'YES' if tier_export_forecasted else 'NO' }}", "")

# 3. Priority Reordering
priority_str = """              * **3. Predictive Export Hold**
                * *Status:* {% if pred_exp_active %}🛑 **HOLDING**{% else %}⚪ False{% endif %}
                * *Values:* 12h Max: {{ max_exp_12h }}c/kWh ≥ {{ pred_exp_thresh }}c/kWh (Release: {{ pred_exp_override }}c/kWh)
              * **4. Predictive Import Hold**
                * *Status:* {% if pred_imp_active %}🛑 **HOLDING**{% else %}⚪ False{% endif %}
                * *Values:* 12h Min: {{ min_imp_12h }}c/kWh ≤ {{ pred_imp_thresh }}c/kWh (Release: {{ pred_imp_override }}c/kWh)
              * **5. Solar Soak Pre-Export**
                * *Status:* {% if soak_exp_active %}☀️ **SOAKING**{% else %}⚪ False{% endif %}
                * *Values:* Window: {{ 'ACTIVE' if neg_forecast_on else 'WAITING' }}, Done Today: {{ 'YES' if completed_today else 'NO' }}, Price: {{ exp_price }}c/kWh ≥ {{ soak_min_price }}c/kWh, SOC: {{ soc }}% > Target {{ soak_target_soc | int(20) }}%"""

new_priority_str = """              * **3. Solar Soak Pre-Export**
                * *Status:* {% if soak_exp_active %}☀️ **SOAKING**{% else %}⚪ False{% endif %}
                * *Values:* Window: {{ 'ACTIVE' if neg_forecast_on else 'WAITING' }}, Done Today: {{ 'YES' if completed_today else 'NO' }}, Price: {{ exp_price }}c/kWh ≥ {{ soak_min_price }}c/kWh, SOC: {{ soc }}% > Target {{ soak_target_soc | int(20) }}%
              * **4. Predictive Export Hold**
                * *Status:* {% if pred_exp_active %}🛑 **HOLDING**{% else %}⚪ False{% endif %}
                * *Values:* 12h Max: {{ max_exp_12h }}c/kWh ≥ {{ pred_exp_thresh }}c/kWh (Release: {{ pred_exp_override }}c/kWh)
              * **5. Predictive Import Hold**
                * *Status:* {% if pred_imp_active %}🛑 **HOLDING**{% else %}⚪ False{% endif %}
                * *Values:* 12h Min: {{ min_imp_12h }}c/kWh ≤ {{ pred_imp_thresh }}c/kWh (Release: {{ pred_imp_override }}c/kWh)"""

# I need to handle the $ symbols first so the replacement matches.
# 4. Remove literal $ signs before {{
content = content.replace("${{", "{{")

# Wait, there are other places with $ like `$15c/kWh`. I should use regex to find $ followed by {{ ... }}
# Already handled by replacing "${{" with "{{"
# Are there cases of "$ " or "$"? 
# Let's do a generic replacement for $ before digits or {{
content = re.sub(r"\$\{\{", r"{{", content)

# But wait, what if they were just hardcoded values?
# Just replace any `$` followed by `{{`
content = content.replace("${{", "{{")

# Re-run priority replacement now that $ is removed
content = re.sub(
    r"\s+\* \*\*3\. Predictive Export Hold\*\*.*?\* \*\*5\. Solar Soak Pre-Export\*\*.*?(?=\n\s+\* \*\*6\. Export Minimum SOC Guard\*\*)",
    "\n" + new_priority_str,
    content,
    flags=re.DOTALL
)

# And fix any leftover $ that were in the original priority text in case my regex missed it
content = content.replace("Price: ${{ exp_price }}", "Price: {{ exp_price }}")

with open(dashboard, "w", encoding="utf-8") as f:
    f.write(content)
print("Done debug_dashboard.yaml")

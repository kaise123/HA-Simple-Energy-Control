import re

filepath = r"c:\Users\Administrator\Github\HA-Simple-Energy-Control\README.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace prices like $0.20/kWh to 20c/kWh
def replace_price(match):
    val_str = match.group(1)
    val = float(val_str)
    # Convert to cents
    cents_val = int(val * 100)
    return f"{cents_val}c/kWh"

content = re.sub(r"\$([0-9\.]+)/kWh", replace_price, content)

# Special cases like `\le \$0.00$/kWh` (from LaTeX style math)
content = content.replace("$\\le \\$0.00$/kWh", "≤ 0c/kWh")
# Also maybe any other weird math blocks
content = content.replace("$\\le \\$", "≤ ")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated README.md")

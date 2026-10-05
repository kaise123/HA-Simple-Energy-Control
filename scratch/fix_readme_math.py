filepath = r"c:\Users\Administrator\Github\HA-Simple-Energy-Control\README.md"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("$\\ge$", "≥")
content = content.replace("$\\le$", "≤")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated ge/le in README.md")

import json

with open("semantic_model.json", encoding="utf-8") as f:
    data = json.load(f)

text = ""

for t in data["tables"]:
    text += f"\nTable: {t['name']}\n"
    text += f"Columns: {', '.join(t['columns'])}\n"

text += "\nRelationships:\n"
text += "\n".join(data["relationships"])

text += "\n\nMeasures:\n"
for m in data["measures"]:
    text += f"{m['name']} = {m['expression']}\n"

with open("semantic_context.txt", "w", encoding="utf-8") as f:
    f.write(text)
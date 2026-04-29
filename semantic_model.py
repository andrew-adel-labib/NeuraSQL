import os
import sys
import pandas as pd
import json

dll_path = r"C:\Program Files\Microsoft.NET\ADOMD.NET\150"
sys.path.append(dll_path)
os.environ["PATH"] += os.pathsep + dll_path

from pyadomd import Pyadomd

conn_str = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/QBS Dashboard;"
    "Catalog=QBS_SighCast_Dashboard;"
)

def fetch(query):
    with Pyadomd(conn_str) as conn:
        with conn.cursor().execute(query) as cur:
            cols = [col[0] for col in cur.description]
            rows = cur.fetchall()
            return pd.DataFrame(rows, columns=cols)

print("Fetching semantic model...")

tables_df = fetch("SELECT * FROM $SYSTEM.TMSCHEMA_TABLES")
columns_df = fetch("SELECT * FROM $SYSTEM.TMSCHEMA_COLUMNS")
relationships_df = fetch("SELECT * FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS")
measures_df = fetch("SELECT * FROM $SYSTEM.TMSCHEMA_MEASURES")

tables = tables_df[["ID", "Name", "IsHidden"]]
tables = tables[tables["IsHidden"] == False]

table_id_map = dict(zip(tables["ID"], tables["Name"]))

print("Available column fields:", columns_df.columns.tolist())

col_name_field = None

if "Name" in columns_df.columns:
    col_name_field = "Name"
elif "ExplicitName" in columns_df.columns:
    col_name_field = "ExplicitName"
else:
    raise Exception("No valid column name field found")

columns_df = columns_df[["TableID", col_name_field, "IsHidden"]]
columns_df = columns_df.rename(columns={col_name_field: "Name"})
columns_df = columns_df[columns_df["IsHidden"] == False]

table_columns = {}

for _, row in columns_df.iterrows():
    table_name = table_id_map.get(row["TableID"])
    if not table_name:
        continue

    table_columns.setdefault(table_name, []).append(row["Name"])

relationships = []

for _, row in relationships_df.iterrows():
    from_table = table_id_map.get(row["FromTableID"])
    to_table = table_id_map.get(row["ToTableID"])

    if from_table and to_table:
        relationships.append(f"{from_table} -> {to_table}")

measures = []

for _, row in measures_df.iterrows():
    if row.get("IsHidden"):
        continue

    measures.append({
        "name": row["Name"],
        "expression": row["Expression"]
    })

semantic_model = {
    "tables": [
        {
            "name": table,
            "columns": cols
        }
        for table, cols in table_columns.items()
    ],
    "relationships": relationships,
    "measures": measures
}

with open("semantic_model.json", "w", encoding="utf-8") as f:
    json.dump(semantic_model, f, indent=2, ensure_ascii=False)
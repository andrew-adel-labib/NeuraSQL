import json
import re
import pandas as pd
from backend.app.llm.groq_client import chat


ARCH_PATH = "DB_Architecture/DB_Architecture.csv"


try:
    df_arch = pd.read_csv(ARCH_PATH)
    df_arch.columns = df_arch.columns.str.strip().str.upper()

    schema_lines = []
    grouped = df_arch.groupby("TABLE_NAME")

    for table, group in grouped:
        columns = ", ".join(group["COLUMN_NAME"].tolist())
        schema_lines.append(f"{table}: {columns}")

    DB_SCHEMA_TEXT = "\n".join(schema_lines)

except Exception as e:
    DB_SCHEMA_TEXT = "Schema not loaded."
    print("Failed to load DB Architecture:", e)


INTERPRET_PROMPT = f"""
You are a forecasting query interpreter.

You MUST choose only from this database schema:

---------------- DATABASE SCHEMA ----------------
{DB_SCHEMA_TEXT}
--------------------------------------------------

Convert the user question into structured JSON:

{{
  "target_table": "",
  "target_column": "",
  "date_column": "",
  "aggregation": "sum",
  "horizon_months": 3
}}

Return ONLY pure JSON.
Do NOT wrap in ```json
Do NOT add explanations.
Do NOT add text before or after JSON.
"""


def clean_json_response(text: str) -> str:
    """
    Remove markdown or `json` wrappers from LLM output.
    """

    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    text = re.sub(r"^json\s*", "", text.strip(), flags=re.IGNORECASE)

    return text.strip()


def interpret(question: str):

    response = chat(
        prompt=question,
        system_prompt=INTERPRET_PROMPT
    )

    cleaned = clean_json_response(response)

    try:
        return json.loads(cleaned)
    except Exception as e:
        raise ValueError(f"LLM returned invalid JSON:\n{cleaned}")
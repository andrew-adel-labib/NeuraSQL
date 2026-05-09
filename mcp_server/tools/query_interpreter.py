import json
import re

from backend.app.llm.client import chat

from mcp_server.tools.schema_retriever import (
    retrieve_schema
)


schema = retrieve_schema()

schema_lines = []

for table in schema["tables"]:

    columns = ", ".join(
        table["columns"]
    )

    schema_lines.append(
        f"{table['name']}: {columns}"
    )

DB_SCHEMA_TEXT = "\n".join(
    schema_lines
)


INTERPRET_PROMPT = f"""
You are an enterprise automotive ERP SQL query interpreter.

You MUST choose ONLY from this database schema.

====================================================
DATABASE SCHEMA
====================================================

{DB_SCHEMA_TEXT}

====================================================

AUTOMOTIVE ERP DOMAINS
====================================================

- Workshop invoices
- Workshop revenue
- Parts inventory
- Parts sales
- Vehicle inventory
- Vehicle sales
- Vehicle profitability
- Mechanics performance
- Branch operations
- Franchise operations

====================================================

Convert the user question into structured JSON.

OUTPUT FORMAT:

{{
    "domain": "",
    "target_tables": [],
    "target_columns": [],
    "measures": [],
    "dimensions": [],
    "filters": {{}},
    "time_context": "",
    "aggregation": "",
    "ranking": false,
    "trend_analysis": false
}}

====================================================
STRICT RULES
====================================================

- ONLY use provided schema
- NEVER invent tables
- NEVER invent columns
- NEVER explain
- Return ONLY JSON
"""


def clean_json_response(text: str):

    text = re.sub(
        r"```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    text = re.sub(
        r"^json\s*",
        "",
        text.strip(),
        flags=re.IGNORECASE
    )

    return text.strip()


def interpret(
    question: str,
    provider: str = "claude"
):

    response = chat(
        prompt=question,
        system_prompt=INTERPRET_PROMPT,
        provider=provider
    )

    cleaned = clean_json_response(
        response
    )

    try:

        return json.loads(cleaned)

    except Exception:

        return {
            "domain": "",
            "target_tables": [],
            "target_columns": [],
            "measures": [],
            "dimensions": [],
            "filters": {},
            "time_context": "",
            "aggregation": "",
            "ranking": False,
            "trend_analysis": False
        }
import json
import re
from typing import Dict

from backend.app.llm.client import chat

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)


def build_schema_context(schema: Dict) -> str:
    """
    Builds semantic schema context:
    - Tables
    - Columns
    - Measures
    - Relationships
    """

    lines = []

    lines.append("TABLES:")

    for table in schema.get("tables", []):

        lines.append(
            f"""
Table: {table.get("name")}

Columns:
{", ".join(table.get("columns", []))}
"""
        )

    lines.append("\nMEASURES:")

    for measure in schema.get(
        "measures",
        []
    ):

        lines.append(
            f"- {measure.get('name')}"
        )

    lines.append("\nRELATIONSHIPS:")

    for rel in schema.get(
        "relationships",
        []
    ):

        lines.append(
            f"- {rel}"
        )

    return "\n".join(lines)


def clean_json(text: str):

    text = text.strip()

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
        r"^json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.strip()

    try:

        return json.loads(text)

    except Exception:

        return None


def rerank_schema(
    query: str,
    schema: Dict,
    model_provider: str = "claude"
):
    """
    Enterprise automotive ERP semantic reranker
    """

    cache_key = (
        f"rerank::{model_provider}::{query}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        return cached

    schema_context = build_schema_context(
        schema
    )

    prompt = f"""
You are an enterprise automotive ERP semantic reranking engine.

Your job:
Analyze the business query and determine the MOST relevant:

1. Tables
2. Dimensions
3. Measures
4. Relationships

====================================================
AUTOMOTIVE ERP DOMAINS
====================================================

Workshop:
- POS_WIPInvoiceHeaders
- POS_WIPInvoiceDetails

Parts Inventory:
- SM_PartsStock

Vehicle Sales:
- VSB_VehicleSalesInvoiceHeaders

Vehicle Inventory:
- VSB_VehicleStock

====================================================
USER QUERY
====================================================

{query}

====================================================
SEMANTIC MODEL
====================================================

{schema_context}

====================================================
STRICT RULES
====================================================

- Use ONLY provided schema
- NEVER invent tables
- NEVER invent columns
- NEVER invent measures
- NEVER invent relationships
- Rank by business relevance
- Prefer exact schema matches
- Include supporting joins when necessary
- Include date/time relevance for trends
- Include branch/company relevance for organizational analysis
- Include vehicle/parts relevance for operational analysis
- Return ONLY JSON

====================================================
OUTPUT FORMAT
====================================================

{{
    "tables": [
        {{
            "name": "",
            "rank": 1,
            "reason": ""
        }}
    ],
    "dimensions": [
        {{
            "table": "",
            "column": "",
            "rank": 1,
            "reason": ""
        }}
    ],
    "measures": [
        {{
            "name": "",
            "rank": 1,
            "reason": ""
        }}
    ],
    "relationships": [
        {{
            "name": "",
            "rank": 1,
            "reason": ""
        }}
    ]
}}
"""

    response = chat(
        prompt=query,
        system_prompt=prompt,
        provider=model_provider
    )

    parsed = clean_json(
        response
    )

    if not parsed:

        parsed = fallback_rerank(
            schema
        )

    parsed["model_provider"] = (
        model_provider
    )

    save_cached_query(
        cache_key,
        parsed
    )

    return parsed


def fallback_rerank(schema: Dict):
    """
    Safe deterministic fallback
    """

    tables = [
        {
            "name": t["name"],
            "rank": i + 1,
            "reason": "Fallback"
        }
        for i, t in enumerate(
            schema.get("tables", [])[:5]
        )
    ]

    dimensions = []

    for t in schema.get(
        "tables",
        []
    )[:5]:

        for col in t.get(
            "columns",
            []
        )[:5]:

            dimensions.append({
                "table": t["name"],
                "column": col,
                "rank": len(dimensions) + 1,
                "reason": "Fallback"
            })

    measures = [
        {
            "name": m["name"],
            "rank": i + 1,
            "reason": "Fallback"
        }
        for i, m in enumerate(
            schema.get("measures", [])[:5]
        )
    ]

    relationships = [
        {
            "name": r,
            "rank": i + 1,
            "reason": "Fallback"
        }
        for i, r in enumerate(
            schema.get("relationships", [])[:5]
        )
    ]

    return {
        "tables": tables,
        "dimensions": dimensions,
        "measures": measures,
        "relationships": relationships
    }


def extract_ranked_components(
    query: str,
    schema: Dict,
    model_provider: str = "claude"
):

    ranked = rerank_schema(
        query,
        schema,
        model_provider=model_provider
    )

    return {
        "tables": ranked.get(
            "tables",
            []
        ),

        "dimensions": ranked.get(
            "dimensions",
            []
        ),

        "measures": ranked.get(
            "measures",
            []
        ),

        "relationships": ranked.get(
            "relationships",
            []
        ),

        "model_provider": model_provider
    }


def get_top_tables(ranked_schema):

    return [
        x["name"]
        for x in ranked_schema.get(
            "tables",
            []
        )
    ]


def get_top_dimensions(ranked_schema):

    return [
        {
            "table": x["table"],
            "column": x["column"]
        }
        for x in ranked_schema.get(
            "dimensions",
            []
        )
    ]


def get_top_measures(ranked_schema):

    return [
        x["name"]
        for x in ranked_schema.get(
            "measures",
            []
        )
    ]


def get_top_relationships(ranked_schema):

    return [
        x["name"]
        for x in ranked_schema.get(
            "relationships",
            []
        )
    ]
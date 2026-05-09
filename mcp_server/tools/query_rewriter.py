import json
import re

from backend.app.llm.client import chat

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)


QUERY_REWRITE_PROMPT = """
You are an enterprise automotive ERP semantic query optimizer.

Your task:
Convert vague business questions into highly structured analytical intent.

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
OBJECTIVES
====================================================

You MUST identify:

1. Business domain
2. Primary measure
3. Dimensions
4. Filters
5. Time grain
6. Ranking intent
7. Trend analysis intent

====================================================
STRICT RULES
====================================================

- Rewrite clearly
- Expand vague business language
- Infer analytical meaning
- Preserve business objective
- Normalize for SQL planning
- DO NOT generate SQL
- Return ONLY rewritten analytical query
"""


QUERY_INTENT_PROMPT = """
You are an enterprise automotive ERP semantic planner.

Convert the user query into structured JSON.

Return ONLY JSON.

OUTPUT FORMAT:

{
    "domain": "",
    "measure": "",
    "dimensions": [],
    "filters": {},
    "time_grain": "",
    "ranking": {
        "enabled": false,
        "type": null,
        "limit": null
    },
    "comparison": false,
    "time_series": false,
    "aggregation": ""
}

STRICT RULES:

- NEVER invent schema
- NEVER invent measures
- NEVER explain
- Return ONLY JSON
"""


def clean_text(text: str) -> str:

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

    return text.strip()


def clean_json(text: str):

    text = clean_text(text)

    try:

        return json.loads(text)

    except Exception:

        return {
            "domain": "",
            "measure": "",
            "dimensions": [],
            "filters": {},
            "time_grain": "",
            "ranking": {
                "enabled": False,
                "type": None,
                "limit": None
            },
            "comparison": False,
            "time_series": False,
            "aggregation": ""
        }


def rewrite_query(
    question: str,
    model_provider: str = "claude"
):

    cache_key = (
        f"rewrite::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        return cached[
            "rewritten_query"
        ]

    rewritten = chat(
        prompt=question,
        system_prompt=QUERY_REWRITE_PROMPT,
        provider=model_provider
    )

    rewritten = clean_text(
        rewritten
    )

    save_cached_query(
        cache_key,
        {
            "rewritten_query": rewritten
        }
    )

    return rewritten


def extract_query_intent(
    question: str,
    model_provider: str = "claude"
):

    cache_key = (
        f"intent::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        return cached

    response = chat(
        prompt=question,
        system_prompt=QUERY_INTENT_PROMPT,
        provider=model_provider
    )

    parsed = clean_json(
        response
    )

    save_cached_query(
        cache_key,
        parsed
    )

    return parsed


def process_query(
    question: str,
    model_provider: str = "claude"
):

    cache_key = (
        f"full_query::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        return cached

    rewritten = rewrite_query(
        question,
        model_provider=model_provider
    )

    intent = extract_query_intent(
        rewritten,
        model_provider=model_provider
    )

    result = {
        "original_query": question,
        "rewritten_query": rewritten,
        "intent": intent,
        "model_provider": model_provider
    }

    save_cached_query(
        cache_key,
        result
    )

    return result
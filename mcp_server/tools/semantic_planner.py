import json
import re

from backend.app.llm.client import chat

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)


def clean_json(text: str):
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

    except:
        return None


def plan_semantics(
    question: str,
    semantic_context: str,
    model_provider: str = "claude"
):
    """
    Enterprise semantic planning:
    Determines:
    - Dimensions
    - Measures
    - Tables
    - Relationships

    Multi-model support:
    - Claude
    - OpenAI
    - Groq

    Uses cache to minimize repeated LLM calls.
    """

    cache_key = (
        f"semantic::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:
        return cached

    system_prompt = f"""
You are an enterprise BI semantic planner.

Your job:
Using the semantic model below:

1. Identify relevant dimensions
2. Identify relevant measures
3. Identify relevant tables
4. Identify required relationships

====================================================
STRICT RULES
====================================================

- ONLY use provided semantic model
- NEVER invent schema
- NEVER invent dimensions
- NEVER invent measures
- NEVER invent relationships
- Include dynamic business hierarchies:
    - Branch
    - Salesman
    - Customer hierarchy
    - Customer channel
    - Item hierarchy
    - Product hierarchy
    - Geographic hierarchy
    - Region
    - District
    - City
    - Area
    - Date hierarchy
- Rank all components by relevance
- Prefer exact schema matches
- Return ONLY JSON

====================================================
OUTPUT FORMAT
====================================================

{{
    "dimensions": [],
    "measures": [],
    "tables": [],
    "relationships": []
}}

====================================================
SEMANTIC MODEL
====================================================

{semantic_context}
"""

    response = chat(
        prompt=question,
        system_prompt=system_prompt,
        provider=model_provider
    )

    parsed = clean_json(
        response
    )

    if parsed:
        parsed["model_provider"] = (
            model_provider
        )

        save_cached_query(
            cache_key,
            parsed
        )

        return parsed

    fallback = {
        "dimensions": [],
        "measures": [],
        "tables": [],
        "relationships": [],
        "model_provider": model_provider
    }

    save_cached_query(
        cache_key,
        fallback
    )

    return fallback
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


def judge_pipeline(
    user_query: str,
    rewritten_query: str,
    semantic_plan: dict,
    dax: str,
    retrieved_rows: list,
    summary: str,
    model_provider: str = "claude"
):
    """
    Enterprise BI QA judge

    Supports:
    - Claude
    - OpenAI
    - Groq

    Evaluates:
    - Query understanding
    - Semantic planning
    - DAX correctness
    - Data relevance
    - Summary quality
    - Final business answer

    Uses cache to avoid repeated QA calls.
    """

    cache_key = (
        f"judge::{model_provider}::{user_query}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:
        return cached

    prompt = f"""
You are an enterprise BI quality assurance judge.

Evaluate the full pipeline quality.

====================================================
USER QUERY
====================================================
{user_query}

====================================================
REWRITTEN QUERY
====================================================
{rewritten_query}

====================================================
SEMANTIC PLAN
====================================================
{json.dumps(semantic_plan, indent=2)}

====================================================
GENERATED DAX
====================================================
{dax}

====================================================
RETRIEVED DATA SAMPLE
====================================================
{retrieved_rows[:10]}

====================================================
FINAL SUMMARY
====================================================
{summary}

====================================================
TASK
====================================================

Evaluate:

1. Query understanding
2. Semantic planning quality
3. DAX correctness
4. Data relevance
5. Summary correctness
6. Business answer quality

====================================================
SCORING RULES
====================================================

- Score between 0.0 and 1.0
- Be strict
- Penalize:
    - hallucination
    - invalid DAX
    - poor semantic planning
    - weak data quality
    - poor summary quality
    - poor business usefulness
- Reward:
    - precise business answers
    - schema correctness
    - strong analytical alignment
    - strategic executive summaries

====================================================
RETURN FORMAT
====================================================

{{
    "overall_score": 0.0,
    "query_understanding": 0.0,
    "semantic_quality": 0.0,
    "dax_quality": 0.0,
    "data_quality": 0.0,
    "summary_quality": 0.0,
    "final_verdict": "",
    "recommendations": []
}}

====================================================
IMPORTANT
====================================================

Return ONLY JSON.
"""

    response = chat(
        prompt=user_query,
        system_prompt=prompt,
        provider=model_provider
    )

    parsed = clean_json(
        response
    )

    if not parsed:
        parsed = {
            "overall_score": 0.5,
            "query_understanding": 0.5,
            "semantic_quality": 0.5,
            "dax_quality": 0.5,
            "data_quality": 0.5,
            "summary_quality": 0.5,
            "final_verdict": (
                "Fallback evaluation"
            ),
            "recommendations": [
                "LLM judge failed; fallback score used."
            ]
        }

    parsed["model_provider"] = (
        model_provider
    )

    save_cached_query(
        cache_key,
        parsed
    )

    return parsed
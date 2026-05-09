import pandas as pd

from backend.app.llm.client import chat

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)


def summarize_answer(
    question: str,
    rows: list,
    model_provider: str = "claude"
):

    if not rows:

        return (
            "No data was returned for this query."
        )

    cache_key = (
        f"summary::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        return cached[
            "summary"
        ]

    df = pd.DataFrame(
        rows
    )

    preview = df.head(
        10
    ).to_dict(
        orient="records"
    )

    prompt = f"""
You are an enterprise AI analytics assistant.

====================================================
USER QUESTION
====================================================

{question}

====================================================
QUERY RESULTS
====================================================

{preview}

====================================================
TASK
====================================================

Provide ONLY:

1. Direct concise answer
2. Maximum 2 short sentences
3. Use simple business language
4. No headings
5. No bullet points
6. No recommendations
7. No KPIs
8. No strategic analysis
9. No executive summary
10. No SQL explanation

====================================================
IMPORTANT
====================================================

Return ONLY the final answer text.
"""

    response = chat(
        prompt=prompt,
        system_prompt=None,
        provider=model_provider
    )

    summary = response.strip()

    save_cached_query(
        cache_key,
        {
            "summary": summary,
            "model_provider": model_provider
        }
    )

    return summary
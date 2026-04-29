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
    """
    Enterprise executive BI summarizer

    Supports:
    - Claude
    - OpenAI
    - Groq

    Features:
    - Cache support
    - Executive summary generation
    - KPI extraction
    - Trend analysis
    - Business recommendations
    """

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
        20
    ).to_dict(
        orient="records"
    )

    prompt = f"""
You are a senior enterprise BI analyst.

Your role:
Provide concise, executive-level business insights from analytical query results.

====================================================
USER QUESTION
====================================================

{question}

====================================================
RETRIEVED DATA SAMPLE
====================================================

{preview}

====================================================
TASK
====================================================

Provide:

1. Direct answer to the business question
2. Key KPIs
3. Important business trends
4. Major anomalies or insights
5. Executive summary
6. Strategic business recommendations if relevant

====================================================
RULES
====================================================

- Be concise
- Be professional
- Be business-oriented
- Focus on decision-making
- Avoid technical explanations
- Avoid SQL/DAX language
- Use natural executive communication
- Prioritize actionable insights
- Return ONLY summary text

====================================================
OUTPUT
====================================================

Return ONLY business summary.
"""

    response = chat(
        prompt=question,
        system_prompt=prompt,
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
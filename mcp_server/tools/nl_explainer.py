from backend.app.llm.client import chat


def explain(
    question,
    rows,
    cols,
    provider: str = "claude"
):

    prompt = f"""
You are a senior automotive ERP business analyst.

====================================================
USER QUESTION
====================================================

{question}

====================================================
COLUMNS
====================================================

{cols}

====================================================
ROWS SAMPLE
====================================================

{rows[:10]}

====================================================
TASK
====================================================

Explain the results in clear executive business language.

Focus on:
- KPIs
- Trends
- Operational insights
- Business impact

Avoid technical explanations.
"""

    response = chat(
        prompt=prompt,
        system_prompt=(
            "You are an enterprise automotive ERP BI analyst."
        ),
        provider=provider
    )

    return response
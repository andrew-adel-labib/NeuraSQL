from backend.app.llm.client import chat


def generate_response(
    question: str,
    rows: list,
    provider: str = "claude"
):
    """
    Enterprise AI business response generator.

    Supports:
    - Claude
    - OpenAI
    - Groq
    """

    if not rows:

        return {
            "answer": "No data was returned for this query.",
            "rows": []
        }

    preview = rows[:15]

    prompt = f"""
You are an enterprise business intelligence analyst.

====================================================
USER QUESTION
====================================================

{question}

====================================================
QUERY RESULTS SAMPLE
====================================================

{preview}

====================================================
TASK
====================================================

Provide:

1. Direct answer to the user's question
2. Important business insights
3. Trends or anomalies
4. Executive-level explanation
5. Actionable recommendations if relevant

====================================================
RULES
====================================================

- Be concise
- Be professional
- Use natural business language
- Avoid technical SQL explanations
- Focus on business insights
- Return ONLY the final answer text
- Prefer KPI-oriented insights
- Highlight profitability and operational efficiency
- Mention revenue impact where relevant
- Prioritize executive summary style

====================================================
OUTPUT
====================================================

Return ONLY the answer.
"""

    answer = chat(
        prompt=prompt,
        system_prompt=None,
        provider=provider
    )

    return {
        "answer": answer.strip(),
        "rows": rows
    }
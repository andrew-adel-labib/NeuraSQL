from backend.app.llm.client import chat

from mcp_server.policies.sql_rules import (
    SQL_SYSTEM_PROMPT
)

from mcp_server.tools.rag_semantic import (
    retrieve_context
)


def clean_sql(sql: str) -> str:

    sql = sql.strip()

    if sql.startswith("```"):

        sql = sql.replace(
            "```sql",
            ""
        )

        sql = sql.replace(
            "```",
            ""
        )

    sql = sql.replace(
        "`",
        ""
    )

    reserved_keywords = [
        "Identity",
        "Order",
        "Group",
        "Key",
        "Value",
        "User"
    ]

    for keyword in reserved_keywords:

        sql = sql.replace(
            f" {keyword} ",
            f" [{keyword}] "
        )

        sql = sql.replace(
            f".{keyword}",
            f".[{keyword}]"
        )

        sql = sql.replace(
            f"({keyword})",
            f"([{keyword}])"
        )

        sql = sql.replace(
            f",{keyword}",
            f",[{keyword}]"
        )

    sql = sql.replace(
        ";",
        ""
    )

    return sql.strip()


def safe_fallback_sql() -> str:

    return """
    SELECT TOP 1
        'System operational' AS Status
    """


def generate_sql(
    question: str,
    model_provider: str = "claude"
) -> str:

    try:

        semantic_context = retrieve_context(
            question
        )

    except Exception:

        semantic_context = ""

    prompt = f"""
{SQL_SYSTEM_PROMPT}

====================================================
SEMANTIC CONTEXT
====================================================

{semantic_context}

====================================================
USER QUESTION
====================================================

{question}

====================================================
IMPORTANT RULES
====================================================

- Return ONLY raw SQL
- No markdown
- No explanations
- SQL Server syntax only
- Use ONLY schema provided
- Never invent tables
- Never invent columns
- ONLY generate SELECT statements
- NEVER generate DELETE
- NEVER generate UPDATE
- NEVER generate INSERT
- NEVER generate DROP
- NEVER generate ALTER
- Prefer business KPIs
- Prefer aggregations
- Prefer joins based on schema

====================================================
OUTPUT
====================================================

Return ONLY SQL query.
"""

    try:

        raw_sql = chat(
            prompt=prompt,
            system_prompt=None,
            provider=model_provider
        )

    except Exception:

        return safe_fallback_sql()

    sql = clean_sql(
        raw_sql
    )

    sql_lower = sql.lower().strip()

    valid_sql = (
        sql_lower.startswith("select")
        or sql_lower.startswith("with")
    )

    if not valid_sql:

        return safe_fallback_sql()

    return sql
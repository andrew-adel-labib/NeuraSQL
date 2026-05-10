import re

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

    sql = sql.replace(
        "[",
        ""
    )

    sql = sql.replace(
        "]",
        ""
    )

    top_match = re.search(
        r"SELECT\s+TOP\s+(\d+)",
        sql,
        re.IGNORECASE
    )

    if top_match:

        limit_value = top_match.group(1)

        sql = re.sub(
            r"SELECT\s+TOP\s+\d+",
            "SELECT",
            sql,
            flags=re.IGNORECASE
        )

        sql += f" LIMIT {limit_value}"

    sql = re.sub(
        r"\bISNULL\s*\(",
        "COALESCE(",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"\bGETDATE\s*\(\s*\)",
        "NOW()",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"ROUND\s*\((.+?),\s*(\d+)\)",
        r"ROUND(CAST(\1 AS NUMERIC), \2)",
        sql,
        flags=re.IGNORECASE
    )

    sql = sql.replace(
        ";",
        ""
    )

    return sql.strip()


def safe_fallback_sql() -> str:

    return """
    SELECT
        'System operational' AS status
    LIMIT 1
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
- PostgreSQL syntax only
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
POSTGRESQL RULES
====================================================

- Use LIMIT instead of TOP
- Use COALESCE instead of ISNULL
- Never use square brackets []
- Use CAST(value AS NUMERIC) before ROUND()
- Never use SQL Server syntax
- Use PostgreSQL-compatible SQL only

GOOD EXAMPLES:

SELECT *
FROM table_name
LIMIT 10

SELECT ROUND(
    CAST(total_amount AS NUMERIC),
    2
)

SELECT COALESCE(quantity, 0)

BAD EXAMPLES:

SELECT TOP 10
ISNULL(quantity, 0)
[column_name]
ROUND(double precision, integer)

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
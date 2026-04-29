# from backend.app.llm.client import chat
# from mcp_server.policies.rules import SQL_SYSTEM_PROMPT
# from backend.app.exceptions import PlanningError
# from rag_semantic import retrieve_context


# def clean_sql(sql: str) -> str:

#     sql = sql.strip()

#     if sql.startswith("```"):
#         sql = sql.replace("```sql", "")
#         sql = sql.replace("```", "")

#     sql = sql.replace("`", "")

#     return sql.strip()


# def generate_sql(question: str) -> str:

#     raw_sql = chat(
#         prompt=question,
#         system_prompt=SQL_SYSTEM_PROMPT
#     )

#     sql = clean_sql(raw_sql)

#     if not (sql.lower().startswith("select") or sql.lower().startswith("with")):
#         raise PlanningError("Only SELECT queries are allowed")

#     return sql


from backend.app.llm.groq_client import chat
from mcp_server.policies.sql_rules import SQL_SYSTEM_PROMPT
from backend.app.exceptions import PlanningError
from rag_semantic import retrieve_context


def clean_sql(sql: str) -> str:

    sql = sql.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")

    sql = sql.replace("`", "")

    return sql.strip()


def generate_sql(question: str) -> str:

    try:
        semantic_context = retrieve_context(question)
    except Exception:
        semantic_context = ""

    prompt = f"""
You are an expert SQL Server query generator using a Power BI semantic model.

SEMANTIC CONTEXT:
{semantic_context}

STRICT RULES:
{SQL_SYSTEM_PROMPT}

USER QUESTION:
{question}

Return ONLY SQL query.
"""

    raw_sql = chat(
        prompt=prompt,
        system_prompt=None
    )

    sql = clean_sql(raw_sql)

    if not (sql.lower().startswith("select") or sql.lower().startswith("with")):
        raise PlanningError("Only SELECT queries are allowed")

    return sql
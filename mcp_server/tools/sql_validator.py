import re
from backend.app.exceptions import SecurityViolation


FORBIDDEN_KEYWORDS = [
    "delete",
    "drop",
    "update",
    "insert",
    "alter",
    "truncate",
    "create",
    "exec",
    "execute",
    "merge"
]


def validate(sql: str):

    sql_clean = sql.strip().lower()

    if not (sql_clean.startswith("select") or sql_clean.startswith("with")):
        raise SecurityViolation(
            "Only SELECT queries are allowed",
            context={"sql_start": sql_clean[:20]}
        )

    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_clean):
            raise SecurityViolation(
                "Dangerous SQL detected",
                context={"keyword": keyword}
            )

    return True
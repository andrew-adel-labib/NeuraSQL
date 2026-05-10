import re

from backend.app.exceptions import (
    SecurityViolation
)


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
    "merge",
    "grant",
    "revoke",
    "deny",
    "backup",
    "restore",
    "shutdown"
]


def validate(sql: str):

    if not sql:

        raise SecurityViolation(
            "Empty SQL query"
        )

    sql_clean = sql.strip().lower()

    sql_clean = re.sub(
        r"\s+",
        " ",
        sql_clean
    )

    if "--" in sql_clean:

        raise SecurityViolation(
            "Inline comments are not allowed"
        )

    if "/*" in sql_clean or "*/" in sql_clean:

        raise SecurityViolation(
            "Block comments are not allowed"
        )

    if ";" in sql_clean[:-1]:

        raise SecurityViolation(
            "Multiple SQL statements are not allowed"
        )

    if not (
        sql_clean.startswith("select")
        or sql_clean.startswith("with")
    ):

        raise SecurityViolation(
            "Only SELECT queries are allowed"
        )

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(pattern, sql_clean):

            raise SecurityViolation(
                "Dangerous SQL detected",
                context={
                    "keyword": keyword
                }
            )

    return True
from backend.app.exceptions import SecurityViolation


def validate_sql(sql: str):
    forbidden = ["delete", "insert", "update", "drop"]
    for f in forbidden:
        if f in sql.lower():
            raise SecurityViolation(
                message="Forbidden SQL operation",
                context={"operation": f},
            )
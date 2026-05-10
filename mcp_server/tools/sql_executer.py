from decimal import Decimal
from datetime import datetime, date

from sqlalchemy import text

from backend.app.db.connection import (
    get_connection
)

from mcp_server.tools.sql_validator import (
    validate
)


def normalize_value(value):

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def execute_sql(sql: str):

    validate(sql)

    conn = get_connection()

    try:

        result = conn.execute(
            text(sql)
        )

        rows_raw = result.fetchall()

        columns = list(result.keys())

        rows = []

        for row in rows_raw:

            record = {}

            for col, value in zip(columns, row):

                record[col] = normalize_value(
                    value
                )

            rows.append(record)

        return rows, columns

    finally:

        conn.close()
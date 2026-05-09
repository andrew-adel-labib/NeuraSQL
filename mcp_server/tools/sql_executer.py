from decimal import Decimal
from datetime import datetime, date
from backend.app.db.connection import get_connection
from mcp_server.tools.sql_validator import validate


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

        cursor = conn.cursor()

        cursor.execute(sql)

        if cursor.description is None:
            return [], []

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = []

        for row in cursor.fetchall():

            record = {}

            for col, value in zip(columns, row):

                record[col] = normalize_value(value)

            rows.append(record)

        cursor.close()

        return rows, columns

    finally:

        conn.close()
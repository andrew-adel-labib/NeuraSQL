from backend.app.db.connection import get_connection
from decimal import Decimal


def execute_sql(sql: str):
    """
    Execute validated SQL query and return rows + columns.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(sql)

    columns = [column[0] for column in cursor.description]

    rows = []
    for row in cursor.fetchall():
        record = {}
        for col, value in zip(columns, row):
            if isinstance(value, Decimal):
                record[col] = float(value)
            else:
                record[col] = value
        rows.append(record)

    conn.close()

    return rows, columns
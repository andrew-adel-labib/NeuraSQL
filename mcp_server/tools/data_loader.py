import pandas as pd

from decimal import Decimal
from datetime import datetime, date

from backend.app.db.connection import (
    get_connection
)


MAX_ROWS_PER_TABLE = 50000


def normalize_value(value):

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def get_all_table_names():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)

    tables = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return tables


def load_table_as_json(
    table_name: str,
    limit: int = MAX_ROWS_PER_TABLE
):

    conn = get_connection()

    cursor = conn.cursor()

    query = f"""
    SELECT TOP {limit} *
    FROM {table_name}
    """

    cursor.execute(query)

    columns = [
        col[0]
        for col in cursor.description
    ]

    rows = []

    for row in cursor.fetchall():

        record = {}

        for col, value in zip(columns, row):

            record[col] = normalize_value(
                value
            )

        rows.append(record)

    conn.close()

    return rows


def load_all_tables_as_json():

    tables = get_all_table_names()

    database_json = {}

    for table in tables:

        try:

            print(
                f"Loading table: {table}"
            )

            database_json[table] = (
                load_table_as_json(table)
            )

        except Exception as e:

            print(
                f"Skipping {table}: {e}"
            )

    return database_json


def load_all_tables_as_dataframe():

    database_json = (
        load_all_tables_as_json()
    )

    database_dfs = {}

    for table, rows in database_json.items():

        try:

            df = pd.DataFrame(rows)

            database_dfs[table] = df

            print(
                f"{table} -> "
                f"{len(df)} rows loaded"
            )

        except Exception as e:

            print(
                f"Could not convert "
                f"{table}: {e}"
            )

    return database_dfs
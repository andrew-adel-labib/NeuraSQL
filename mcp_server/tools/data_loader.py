import json
import pandas as pd
from decimal import Decimal
from backend.app.db.connection import get_connection


def get_all_table_names():
    """
    Get all user tables in the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
    """)

    tables = [row[0] for row in cursor.fetchall()]

    conn.close()
    return tables


def load_table_as_json(table_name: str):
    """
    Load single table and return JSON serializable list of dicts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")

    columns = [col[0] for col in cursor.description]

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

    return rows


def load_all_tables_as_json():
    """
    Load entire database into dictionary of table_name → JSON rows
    """
    tables = get_all_table_names()

    database_json = {}

    for table in tables:
        try:
            database_json[table] = load_table_as_json(table)
        except Exception as e:
            print(f"Skipping table {table}: {e}")

    return database_json


def load_all_tables_as_dataframe():
    """
    Load entire database and return:
    table_name → pandas DataFrame
    """

    database_json = load_all_tables_as_json()

    database_dfs = {}

    for table, rows in database_json.items():
        try:
            df = pd.DataFrame(rows)
            database_dfs[table] = df
        except Exception as e:
            print(f"Could not convert {table} to DataFrame: {e}")

    return database_dfs
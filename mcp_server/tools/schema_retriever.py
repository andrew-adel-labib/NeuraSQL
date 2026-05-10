from sqlalchemy import text

from backend.app.db.connection import (
    get_connection
)


def retrieve_schema():

    conn = get_connection()

    query = """
    SELECT
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY
        table_name,
        ordinal_position
    """

    result = conn.execute(
        text(query)
    )

    rows = result.fetchall()

    schema = {
        "tables": []
    }

    table_map = {}

    for row in rows:

        table_name = row.table_name

        if table_name not in table_map:

            table_obj = {
                "name": table_name,
                "columns": []
            }

            schema["tables"].append(
                table_obj
            )

            table_map[table_name] = table_obj

        table_map[table_name]["columns"].append(
            row.column_name
        )

    conn.close()

    return schema


if __name__ == "__main__":

    import json

    schema = retrieve_schema()

    print(
        json.dumps(
            schema,
            indent=2
        )
    )
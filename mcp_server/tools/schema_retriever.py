from backend.app.db.connection import get_connection


def retrieve_schema():

    conn = get_connection()

    cursor = conn.cursor()

    query = """
    SELECT
        t.name AS table_name,
        c.name AS column_name,
        ty.name AS data_type
    FROM sys.tables t
    INNER JOIN sys.columns c
        ON t.object_id = c.object_id
    INNER JOIN sys.types ty
        ON c.user_type_id = ty.user_type_id
    ORDER BY
        t.name,
        c.column_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

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
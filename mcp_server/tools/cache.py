DATABASE_CACHE = {}


def load_cache():

    from mcp_server.tools.data_loader import (
        load_all_tables_as_dataframe
    )

    global DATABASE_CACHE

    DATABASE_CACHE = (
        load_all_tables_as_dataframe()
    )

    print("\nLoaded tables into memory cache:\n")

    for table_name, df in DATABASE_CACHE.items():

        print(
            f"{table_name} -> "
            f"{len(df)} rows"
        )


def get_cache():

    return DATABASE_CACHE


def clear_cache():

    global DATABASE_CACHE

    DATABASE_CACHE = {}

    print("Cache cleared.")
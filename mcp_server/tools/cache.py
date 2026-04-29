DATABASE_CACHE = {}


def load_cache():
    from mcp_server.tools.data_loader import load_all_tables_as_dataframe

    global DATABASE_CACHE
    DATABASE_CACHE = load_all_tables_as_dataframe()

    print("Loaded tables into cache:")
    print(list(DATABASE_CACHE.keys()))


def get_cache():
    return DATABASE_CACHE
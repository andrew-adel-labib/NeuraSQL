import pyodbc
from backend.app.config import settings


def get_connection():
    """
    Create MSSQL connection using environment variables.
    """

    connection_string = (
        f"DRIVER={{{settings.DB_DRIVER}}};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_NAME};"
        f"Trusted_Connection={settings.DB_TRUSTED_CONNECTION};"
    )

    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")
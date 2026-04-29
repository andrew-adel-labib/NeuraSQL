import os
import sys
import logging
import clr
import pandas as pd
from datetime import datetime
from decimal import Decimal
from mcp_server.tools.dax_validator import validate_dax, DAXValidationError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dax_executor")

DLL_DIR = r"C:\Program Files\Microsoft.NET\ADOMD.NET\160"

sys.path.append(DLL_DIR)
os.environ["PATH"] += os.pathsep + DLL_DIR

import clr
clr.AddReference("Microsoft.AnalysisServices.AdomdClient")

if not os.path.exists(DLL_DIR):
    raise RuntimeError(
        f"ADOMD client not found at {DLL_DIR}. "
        f"Install 'Microsoft Analysis Services OLE DB 19'."
    )

sys.path.append(DLL_DIR)
os.environ["PATH"] += os.pathsep + DLL_DIR

DLL_FILE = os.path.join(DLL_DIR, "Microsoft.AnalysisServices.AdomdClient.dll")

try:
    clr.AddReference(DLL_FILE)
except Exception as e:
    raise RuntimeError(f"Failed to load ADOMD DLL: {str(e)}")


from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand


CONN_STR = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/QBS Dashboard;"
    "Catalog=QBS_SighCast_Dashboard;"
)


def normalize_value(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, datetime):
        return value.isoformat()

    return value


def execute_dax(dax: str):
    """
    Execute DAX query on Power BI semantic model
    Returns: rows, columns
    """

    try:
        validate_dax(dax)

        logger.info("Executing DAX query...")
        logger.info(dax)

        conn = AdomdConnection(CONN_STR)

        try:
            conn.Open()

            cmd = AdomdCommand(dax, conn)
            reader = cmd.ExecuteReader()

            columns = [reader.GetName(i) for i in range(reader.FieldCount)]

            rows = []

            while reader.Read():
                record = {}

                for i, col in enumerate(columns):
                    record[col] = normalize_value(reader[i])

                rows.append(record)

            reader.Close()
            conn.Close()

            logger.info(f"Returned {len(rows)} rows")

            return rows, columns

        finally:
            if conn.State != 0:
                conn.Close()

    except DAXValidationError as e:
        logger.error(f"DAX validation failed: {str(e)}")
        raise

    except Exception as e:
        logger.exception("DAX execution failed")
        raise RuntimeError(f"DAX execution error: {str(e)}")
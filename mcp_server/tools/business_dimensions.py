import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

SQL_DIMENSION_QUERIES = {
    "customer_category": """
        SELECT DISTINCT Category
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE Category IS NOT NULL
    """,

    "customer_category2": """
        SELECT DISTINCT Category2
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE Category2 IS NOT NULL
    """,

    "customer_category3": """
        SELECT DISTINCT Category3
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE Category3 IS NOT NULL
    """,

    "customer_category4": """
        SELECT DISTINCT Category4
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE Category4 IS NOT NULL
    """,

    "item_category1": """
        SELECT DISTINCT Category1
        FROM QBS.dbo.QBS_SighCast_Item
        WHERE Category1 IS NOT NULL
    """,

    "item_category2": """
        SELECT DISTINCT Category2
        FROM QBS.dbo.QBS_SighCast_Item
        WHERE Category2 IS NOT NULL
    """,

    "item_category3": """
        SELECT DISTINCT Category3
        FROM QBS.dbo.QBS_SighCast_Item
        WHERE Category3 IS NOT NULL
    """,

    "item_category4": """
        SELECT DISTINCT Category4
        FROM QBS.dbo.QBS_SighCast_Item
        WHERE Category4 IS NOT NULL
    """,

    "branches": """
        SELECT DISTINCT Branch_Name
        FROM QBS.dbo.QBS_SighCast_Branch
        WHERE Branch_Name IS NOT NULL
    """,

    "company_codes": """
        SELECT DISTINCT CompanyCode
        FROM QBS.dbo.QBS_SighCast_Company
        WHERE CompanyCode IS NOT NULL
    """,

    "areas": """
        SELECT DISTINCT AreaNo
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE AreaNo IS NOT NULL
    """,

    "cities": """
        SELECT DISTINCT CityNo
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE CityNo IS NOT NULL
    """,

    "districts": """
        SELECT DISTINCT DistrictNo
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE DistrictNo IS NOT NULL
    """,

    "regions": """
        SELECT DISTINCT RegionNo
        FROM QBS.dbo.QBS_SighCast_Customer
        WHERE RegionNo IS NOT NULL
    """,

    "salesmen": """
        SELECT DISTINCT SalesmanNameA
        FROM QBS.dbo.QBS_SighCast_Salesman
        WHERE SalesmanNameA IS NOT NULL
    """
}


def get_sql_connection():
    driver = os.getenv("DB_DRIVER")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes")

    if not all([driver, server, database]):
        raise ValueError(
            "Missing DB config in .env"
        )

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection={trusted};"
        f"TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)


def extract_business_dimensions():
    """
    Extract only business dimension values from SQL Server QBS DB
    for semantic enrichment.
    """

    conn = get_sql_connection()
    cursor = conn.cursor()

    extracted_dimensions = {}

    try:
        for dimension_name, query in SQL_DIMENSION_QUERIES.items():

            cursor.execute(query)

            rows = cursor.fetchall()

            extracted_dimensions[dimension_name] = sorted(
                list({
                    str(row[0]).strip()
                    for row in rows
                    if row[0] is not None
                    and str(row[0]).strip() != ""
                })
            )

    finally:
        conn.close()

    return extracted_dimensions


if __name__ == "__main__":
    import json

    print("Extracting business dimensions from QBS database...")

    dimensions = extract_business_dimensions()

    print(
        json.dumps(
            dimensions,
            indent=2,
            ensure_ascii=False
        )
    )
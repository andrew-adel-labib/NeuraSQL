from sqlalchemy import text

from backend.app.db.connection import (
    get_connection
)


SQL_DIMENSION_QUERIES = {

    "branches": """
        SELECT DISTINCT System_Branch_Name
        FROM POS_WIPInvoiceHeaders
        WHERE System_Branch_Name IS NOT NULL
    """,

    "companies": """
        SELECT DISTINCT System_Company_Name
        FROM POS_WIPInvoiceHeaders
        WHERE System_Company_Name IS NOT NULL
    """,

    "entities": """
        SELECT DISTINCT LegelEntity_Name
        FROM POS_WIPInvoiceHeaders
        WHERE LegelEntity_Name IS NOT NULL
    """,

    "departments": """
        SELECT DISTINCT Department
        FROM POS_WIPInvoiceHeaders
        WHERE Department IS NOT NULL
    """,

    "franchises": """
        SELECT DISTINCT Franchise_Code
        FROM POS_WIPInvoiceHeaders
        WHERE Franchise_Code IS NOT NULL
    """,

    "sale_types": """
        SELECT DISTINCT Sale_Type
        FROM POS_WIPInvoiceHeaders
        WHERE Sale_Type IS NOT NULL
    """,

    "vehicle_models": """
        SELECT DISTINCT Model
        FROM POS_WIPInvoiceHeaders
        WHERE Model IS NOT NULL
    """,

    "mechanics": """
        SELECT DISTINCT WL_Mechanic1
        FROM POS_WIPInvoiceDetails
        WHERE WL_Mechanic1 IS NOT NULL
    """,

    "parts": """
        SELECT DISTINCT PartNo_RTSCode
        FROM POS_WIPInvoiceDetails
        WHERE PartNo_RTSCode IS NOT NULL
    """,

    "vehicle_numbers": """
        SELECT DISTINCT Vehicle_Number
        FROM VSB_VehicleStock
        WHERE Vehicle_Number IS NOT NULL
    """,

    "vehicle_types": """
        SELECT DISTINCT Vehicle_Type
        FROM VSB_VehicleStock
        WHERE Vehicle_Type IS NOT NULL
    """,

    "vehicle_locations": """
        SELECT DISTINCT Vehicle_Location
        FROM VSB_VehicleStock
        WHERE Vehicle_Location IS NOT NULL
    """,

    "parts_categories": """
        SELECT DISTINCT Parts_Category
        FROM SM_PartsStock
        WHERE Parts_Category IS NOT NULL
    """
}


def extract_business_dimensions():

    conn = get_connection()

    extracted_dimensions = {}

    try:

        for dimension_name, query in (
            SQL_DIMENSION_QUERIES.items()
        ):

            result = conn.execute(
                text(query)
            )

            rows = result.fetchall()

            extracted_dimensions[
                dimension_name
            ] = sorted(
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

    dimensions = (
        extract_business_dimensions()
    )

    print(
        json.dumps(
            dimensions,
            indent=2,
            ensure_ascii=False
        )
    )
import json
import re

from backend.app.llm.client import chat

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)


def clean_json(text: str):

    text = re.sub(
        r"```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    text = re.sub(
        r"^json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.strip()

    try:

        return json.loads(text)

    except Exception:

        return None


def plan_semantics(
    question: str,
    semantic_context: str,
    model_provider: str = "claude"
):
    """
    Enterprise automotive ERP semantic planner
    """

    cache_key = (
        f"semantic::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        return cached

    system_prompt = f"""
You are an enterprise automotive ERP semantic planner.

Your job:
Using the semantic model below, identify the most relevant:

1. Tables
2. Dimensions
3. Measures
4. Relationships
5. Filters
6. Aggregations
7. Time intelligence requirements

====================================================
AUTOMOTIVE ERP BUSINESS DOMAINS
====================================================

WORKSHOP OPERATIONS
-------------------
Tables:
- POS_WIPInvoiceHeaders
- POS_WIPInvoiceDetails

Business Concepts:
- Workshop revenue
- Invoice analysis
- Labour analysis
- Mechanic performance
- Service profitability
- VAT analysis
- Branch workshop performance

====================================================

PARTS INVENTORY
---------------
Tables:
- SM_PartsStock

Business Concepts:
- Inventory valuation
- Parts availability
- Stock quantity
- Stock movement
- Parts profitability
- Parts categories
- Branch inventory analysis

====================================================

VEHICLE SALES
-------------
Tables:
- VSB_VehicleSalesInvoiceHeaders

Business Concepts:
- Vehicle sales revenue
- Vehicle invoice analysis
- Sales performance
- Sales trends
- Company performance

====================================================

VEHICLE INVENTORY
-----------------
Tables:
- VSB_VehicleStock

Business Concepts:
- Vehicle inventory
- Vehicle profitability
- Stock valuation
- Vehicle location analysis
- New vs used vehicle analysis
- Vehicle availability
- Branch inventory performance

====================================================
KNOWN RELATIONSHIPS
====================================================

Workshop Details → Workshop Headers

POS_WIPInvoiceDetails.WIPInvoiceHeader_ID
=
POS_WIPInvoiceHeaders.ID

Alternative:
POS_WIPInvoiceDetails.WIP_Number
=
POS_WIPInvoiceHeaders.WIP_Number

====================================================

Workshop Parts → Parts Inventory

POS_WIPInvoiceDetails.PartNo_RTSCode
=
SM_PartsStock.Part_Number

====================================================

Vehicle Sales → Vehicle Stock

VSB_VehicleSalesInvoiceHeaders.Vehicle_Number
=
VSB_VehicleStock.Vehicle_Number

Alternative:
VSB_VehicleSalesInvoiceHeaders.VehicleStock_SequenceNumber
=
VSB_VehicleStock.Stock_Sequence_Number

====================================================
IMPORTANT DIMENSIONS
====================================================

Organizational:
- System_Company_Name
- System_Branch_Name
- LegelEntity_Name

Operational:
- Department
- Franchise_Code
- Sale_Type
- LabourType_Code
- LabourAnalysis_Code

Inventory:
- Parts_Category
- Vehicle_Type
- Vehicle_Location

Vehicle:
- Vehicle_Number
- Vehicle_Identification_Number
- Registration_Number
- New_or_Used_Vehicle

Time:
- RunDate
- Dateof_Invoice
- Invoice_Date
- Delivery_Date

====================================================
IMPORTANT MEASURES
====================================================

Workshop Revenue:
SUM(Net_Value)

Workshop Gross Revenue:
SUM(Gross_Value)

Workshop VAT:
SUM(Invoice_VAT)

Parts Revenue:
SUM(Selling_Price)

Parts Cost:
SUM(Cost_Price)

Parts Quantity:
SUM(PartQuantity)

Inventory Value:
SUM(Stock_Value)

Vehicle Sales Revenue:
SUM(Invoice_Value)

Vehicle Profit:
SUM(Total_Profit_Value)

Vehicle Stock Value:
SUM(Stock_Value)

====================================================
STRICT RULES
====================================================

- ONLY use provided semantic model
- PostgreSQL syntax only
- Use LIMIT instead of TOP
- Use NOW() instead of GETDATE()
- Use DATE_TRUNC for time grouping
- Use ILIKE for case-insensitive search
- NEVER invent:
    - tables
    - columns
    - joins
    - measures
    - filters
- Prefer exact schema matches
- Prefer operational KPIs
- Prefer correct business relationships
- Use ONLY valid PostgreSQL business logic
- Rank components by relevance
- Return ONLY JSON

====================================================
OUTPUT FORMAT
====================================================

{{
    "dimensions": [],
    "measures": [],
    "tables": [],
    "joins": [],
    "filters": [],
    "aggregations": [],
    "time_context": []
}}

====================================================
SEMANTIC MODEL
====================================================

{semantic_context}
"""

    response = chat(
        prompt=question,
        system_prompt=system_prompt,
        provider=model_provider
    )

    parsed = clean_json(
        response
    )

    if parsed:

        parsed["model_provider"] = (
            model_provider
        )

        save_cached_query(
            cache_key,
            parsed
        )

        return parsed

    fallback = {
        "dimensions": [],
        "measures": [],
        "tables": [],
        "joins": [],
        "filters": [],
        "aggregations": [],
        "time_context": [],
        "model_provider": model_provider
    }

    save_cached_query(
        cache_key,
        fallback
    )

    return fallback
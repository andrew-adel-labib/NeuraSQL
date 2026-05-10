import json
import re

from backend.app.llm.client import chat

from mcp_server.tools.business_dimensions import (
    extract_business_dimensions
)

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)


DIMENSION_SELECTOR_PROMPT = """
You are an enterprise automotive ERP semantic planner.

Your task:
Analyze the business question using ONLY:

1. Retrieved business dimensions from production database
2. Semantic schema context
3. Automotive ERP business logic

====================================================
AUTOMOTIVE BUSINESS DOMAINS
====================================================

- Workshop revenue
- Workshop invoices
- Parts inventory
- Parts sales
- Vehicle inventory
- Vehicle sales
- Vehicle profitability
- Mechanics performance
- Branch operations
- Franchise operations

====================================================
STRICT RULES
====================================================

- ONLY use provided dimensions
- ONLY use provided schema
- NEVER invent:
    - dimensions
    - branches
    - companies
    - franchises
    - mechanics
    - vehicles
    - filters
- Detect:
    - measures
    - dimensions
    - filters
    - grain
    - ranking
    - aggregation
    - trend analysis
- Return ONLY JSON
- PostgreSQL analytical environment
- PostgreSQL-compatible dimension planning

====================================================
OUTPUT FORMAT
====================================================

{
    "measure": "",
    "dimensions": [],
    "filters": {},
    "grain": "",
    "aggregation": "",
    "ranking": {
        "enabled": false,
        "type": null,
        "limit": null
    },
    "time_series": false
}
"""


def clean_json(text: str):

    text = text.strip()

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


def build_business_dimension_context():

    dimensions = extract_business_dimensions()

    lines = []

    DIMENSION_LABELS = {

        "branches": "Branch",

        "companies": "Company",

        "entities": "Entity",

        "departments": "Department",

        "franchises": "Franchise",

        "sale_types": "Sale Type",

        "vehicle_models": "Vehicle Model",

        "mechanics": "Mechanic",

        "parts": "Part",

        "vehicle_numbers": "Vehicle",

        "vehicle_types": "Vehicle Type",

        "vehicle_locations": "Vehicle Location",

        "parts_categories": "Parts Category"
    }

    for key, values in dimensions.items():

        label = DIMENSION_LABELS.get(
            key,
            key
        )

        sample_values = values[:100]

        lines.append(
            f"""
Dimension: {label}

Possible Values:
{", ".join(map(str, sample_values))}
"""
        )

    return "\n".join(lines)


def fallback_dimension_plan(
    question: str,
    business_dimensions: dict
):

    q = question.lower()

    dimensions = []

    filters = {}

    grain = None

    aggregation = "sum"

    ranking = {
        "enabled": False,
        "type": None,
        "limit": None
    }

    measure = "Workshop Revenue"

    if "vehicle" in q:

        measure = "Vehicle Sales Revenue"

    elif "inventory" in q:

        measure = "Inventory Value"

    elif "parts" in q:

        measure = "Parts Revenue"

    elif "profit" in q:

        measure = "Vehicle Profit"

    if "branch" in q:
        dimensions.append("Branch")

    if "company" in q:
        dimensions.append("Company")

    if "franchise" in q:
        dimensions.append("Franchise")

    if "mechanic" in q:
        dimensions.append("Mechanic")

    for branch in business_dimensions.get(
        "branches",
        []
    ):

        if branch.lower() in q:

            filters["Branch"] = branch
            break

    for company in business_dimensions.get(
        "companies",
        []
    ):

        if company.lower() in q:

            filters["Company"] = company
            break

    if "last year" in q:

        filters["Year"] = "last_year"

    elif "this year" in q:

        filters["Year"] = "current_year"

    if any(
        x in q
        for x in [
            "month",
            "trend"
        ]
    ):

        grain = "month"

    elif "quarter" in q:

        grain = "quarter"

    elif "year" in q:

        grain = "year"

    if "top" in q:

        ranking = {
            "enabled": True,
            "type": "top",
            "limit": 10
        }

    elif "bottom" in q:

        ranking = {
            "enabled": True,
            "type": "bottom",
            "limit": 10
        }

    return {
        "measure": measure,
        "dimensions": dimensions,
        "filters": filters,
        "grain": grain,
        "aggregation": aggregation,
        "ranking": ranking,
        "time_series": grain in [
            "month",
            "quarter",
            "year"
        ]
    }


def select_dimensions(
    question: str,
    context: str,
    model_provider: str = "claude"
):
    """
    Enterprise automotive ERP semantic planner
    """

    cache_key = (
        f"dimension::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:

        cached["filters"] = cached.get(
            "filters",
            {}
        )

        return cached

    business_dimensions = (
        extract_business_dimensions()
    )

    business_context = (
        build_business_dimension_context()
    )

    prompt = f"""
{DIMENSION_SELECTOR_PROMPT}

====================================================
BUSINESS DIMENSIONS
====================================================

{business_context}

====================================================
SEMANTIC CONTEXT
====================================================

{context}

====================================================
USER QUESTION
====================================================

{question}
"""

    response = chat(
        prompt=question,
        system_prompt=prompt,
        provider=model_provider
    )

    parsed = clean_json(
        response
    )

    if parsed:

        parsed["filters"] = parsed.get(
            "filters",
            {}
        )

        parsed["model_provider"] = (
            model_provider
        )

        save_cached_query(
            cache_key,
            parsed
        )

        return parsed

    fallback = fallback_dimension_plan(
        question,
        business_dimensions
    )

    fallback["filters"] = fallback.get(
        "filters",
        {}
    )

    fallback["model_provider"] = (
        model_provider
    )

    save_cached_query(
        cache_key,
        fallback
    )

    return fallback

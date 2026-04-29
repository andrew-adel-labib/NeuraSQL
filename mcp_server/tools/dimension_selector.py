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

from mcp_server.tools.business_dimension_mapper import (
    correct_user_dimension_filters
)


DIMENSION_SELECTOR_PROMPT = """
You are an enterprise BI semantic planner.

Your task:
Analyze the business question using ONLY:

1. Retrieved business dimensions from production database
2. Semantic schema context
3. Ranked measures

====================================================
STRICT RULES
====================================================

- ONLY use provided dimensions
- ONLY use provided schema
- ONLY use provided measures
- NEVER invent:
    - dimensions
    - branches
    - categories
    - products
    - geography
    - salesmen
    - filters
- If user mentions:
    - branch
    - city
    - region
    - customer channel
    - product hierarchy
    - salesman
  then map ONLY to actual retrieved DB values
- Detect:
    - measure
    - dimensions
    - filters
    - grain
    - ranking
    - aggregation
    - time series
- Return ONLY JSON

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
    """
    Builds production business dimension metadata
    with clear dimension-to-values mapping
    """

    dimensions = extract_business_dimensions()

    lines = []

    DIMENSION_LABELS = {
        "branches": "Branch",
        "salesmen": "Salesman",
        "regions": "Region",
        "districts": "District",
        "cities": "City",
        "areas": "Area",

        "customer_category": "Customer Channel",
        "customer_category2": "Customer Sub-Channel",
        "customer_category3": "Customer Level 3",
        "customer_category4": "Customer Level 4",

        "item_category1": "Master Brand",
        "item_category2": "Sub Brand",
        "item_category3": "Item Level 3",
        "item_category4": "Item Level 4",

        "company_codes": "Company"
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

    measure = "SalesBeforeTax"

    if any(
        x in q
        for x in [
            "volume",
            "qty",
            "quantity",
            "ton"
        ]
    ):
        measure = "Sales QTY Ton"

    if "branch" in q:
        dimensions.append("Branch")

    if any(
        x in q
        for x in [
            "region",
            "district",
            "city",
            "area"
        ]
    ):
        dimensions.append("Geographic")

    if any(
        x in q
        for x in [
            "channel",
            "customer"
        ]
    ):
        dimensions.append("Customer Channel")

    if any(
        x in q
        for x in [
            "product",
            "brand",
            "item"
        ]
    ):
        dimensions.append("Item Hierarchy")

    for branch in business_dimensions.get(
        "branches",
        []
    ):
        if branch.lower() in q:
            filters["Branch"] = branch
            break

    for city in business_dimensions.get(
        "cities",
        []
    ):
        if str(city).lower() in q:
            filters["City"] = city
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
    Enterprise production semantic dimension selector
    Supports:
    - Claude
    - OpenAI
    - Groq
    """

    cache_key = (
        f"dimension::{model_provider}::{question}"
    )

    cached = load_cached_query(
        cache_key
    )

    if cached:
        cached["filters"] = correct_user_dimension_filters(
            cached.get("filters", {})
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
        parsed["filters"] = correct_user_dimension_filters(
            parsed.get("filters", {})
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

    fallback["filters"] = (
        correct_user_dimension_filters(
            fallback.get("filters", {})
        )
    )

    fallback["model_provider"] = (
        model_provider
    )

    save_cached_query(
        cache_key,
        fallback
    )

    return fallback
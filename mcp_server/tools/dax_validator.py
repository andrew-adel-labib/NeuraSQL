import re
import json
import os



BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SCHEMA_PATH = os.path.join(
    BASE_DIR,
    "../../semantic_model.json"
)



class DAXValidationError(Exception):
    pass



def load_semantic_model():
    try:
        with open(
            SCHEMA_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return {}



def validate_known_tables(
    dax: str,
    model: dict
):
    """
    Ensures all referenced tables exist
    in semantic_model.json
    """

    known_tables = [
        t["name"].lower()
        for t in model.get(
            "tables",
            []
        )
    ]

    referenced_tables = re.findall(
        r"'([^']+)'",
        dax
    )

    for table in referenced_tables:
        if table.lower() not in known_tables:
            raise DAXValidationError(
                f"Unknown semantic model table detected: {table}"
            )


def validate_known_measures(
    dax: str,
    model: dict
):
    """
    Optional measure validation
    """

    known_measures = [
        m["name"].lower()
        for m in model.get(
            "measures",
            []
        )
    ]

    referenced_measures = re.findall(
        r"\[([^\]]+)\]",
        dax
    )

    for measure in referenced_measures:

        if measure.lower() in known_measures:
            continue

        if any(
            measure.lower() in c.lower()
            for t in model.get(
                "tables",
                []
            )
            for c in t.get(
                "columns",
                []
            )
        ):
            continue

        if measure.lower() == "metric":
            continue

        raise DAXValidationError(
            f"Unknown measure/column detected: {measure}"
        )



def validate_dax(
    dax: str
):
    """
    Enterprise-grade DAX validator:
    - Structural validation
    - Dynamic semantic schema validation
    - Hallucination prevention
    - Complexity checks
    - Filter enforcement
    """

    if not dax:
        raise DAXValidationError(
            "Empty DAX query"
        )

    dax = dax.strip()
    dax_lower = dax.lower()

    model = load_semantic_model()

    if not model:
        raise DAXValidationError(
            "Semantic model could not be loaded"
        )

    if not dax_lower.startswith(
        "evaluate"
    ):
        raise DAXValidationError(
            "DAX must start with EVALUATE"
        )

    if "summarizecolumns" not in dax_lower:
        raise DAXValidationError(
            "DAX must use SUMMARIZECOLUMNS"
        )

    if " where " in dax_lower:
        raise DAXValidationError(
            "WHERE is not allowed in DAX"
        )

    if re.search(
        r"year\s*\(\s*max\s*\(",
        dax,
        re.IGNORECASE
    ):
        raise DAXValidationError(
            "YEAR(MAX(...)) is invalid"
        )

    if (
        re.search(
            r"month\s*\(",
            dax,
            re.IGNORECASE
        )
        and "summarizecolumns" in dax_lower
    ):
        raise DAXValidationError(
            "MONTH() cannot be direct grouping column"
        )

    hallucinated_tables = [
        "branchdim",
        "datedimensions",
        "salesdim",
        "customerdim",
        "productdim",
        "'date'",
        "'sales'",
        "'branchdim'"
    ]

    for bad_table in hallucinated_tables:
        if bad_table in dax_lower:
            raise DAXValidationError(
                f"Hallucinated table detected: {bad_table}"
            )

    validate_known_tables(
        dax,
        model
    )

    validate_known_measures(
        dax,
        model
    )

    if re.search(
        r"var\s+\w+\s*=",
        dax,
        re.IGNORECASE
    ):
        raise DAXValidationError(
            "VAR blocks not allowed for standard BI queries"
        )

    if re.search(
        r"return\s+\w+",
        dax,
        re.IGNORECASE
    ):
        raise DAXValidationError(
            "RETURN blocks indicate over-complex DAX"
        )

    if (
        "'datedim'[year]" in dax_lower
        and "filter(" not in dax_lower
    ):
        raise DAXValidationError(
            "DateDim year filters must use FILTER()"
        )

    if re.search(
        r"filter\s*\(\s*all\s*\('datedim'\)\s*,\s*filter\s*\(",
        dax,
        re.IGNORECASE | re.DOTALL
    ):
        raise DAXValidationError(
            "Nested DateDim FILTER duplication detected"
        )

    if dax.count("(") != dax.count(")"):
        raise DAXValidationError(
            "Unbalanced parentheses"
        )

    if "month" in dax_lower or "year" in dax_lower:
        if "summarizecolumns" not in dax_lower:
            raise DAXValidationError(
                "Trend queries must use SUMMARIZECOLUMNS"
            )

    if re.search(
        r"related\s*\(",
        dax,
        re.IGNORECASE
    ):
        raise DAXValidationError(
            "RELATED() should not be necessary"
        )

    complexity_score = 0

    complexity_score += len(
        re.findall(
            r"\bcalculate\b",
            dax_lower
        )
    )

    complexity_score += len(
        re.findall(
            r"\bvar\b",
            dax_lower
        )
    )

    complexity_score += len(
        re.findall(
            r"\breturn\b",
            dax_lower
        )
    )

    complexity_score += len(
        re.findall(
            r"\baddcolumns\b",
            dax_lower
        )
    )

    if complexity_score > 3:
        raise DAXValidationError(
            "DAX query is unnecessarily complex"
        )

    return {
        "valid": True,
        "complexity_score": complexity_score,
        "starts_correctly": True,
        "uses_summarizecolumns": True,
        "hallucination_check": "passed",
        "dynamic_schema_check": "passed",
        "measure_validation": "passed",
        "filter_structure": "passed"
    }
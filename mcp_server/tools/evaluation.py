import re
from typing import Dict, Optional


def evaluate_pipeline(
    user_query: str,
    rewritten: str,
    semantic_plan: Dict,
    sql: str,
    validation: Optional[Dict] = None,
    retrieved_rows: Optional[list] = None,
    tables: Optional[list] = None,
    dimensions: Optional[list] = None,
    measures: Optional[list] = None,
    joins: Optional[list] = None,
    provider: str = "claude"
):
    """
    Enterprise SQL pipeline evaluation layer
    """

    validation = validation or {}

    retrieved_rows = retrieved_rows or []

    tables = tables or semantic_plan.get(
        "tables",
        []
    )

    dimensions = dimensions or semantic_plan.get(
        "dimensions",
        []
    )

    measures = measures or semantic_plan.get(
        "measures",
        []
    )

    joins = joins or semantic_plan.get(
        "joins",
        []
    )

    score = 0.0

    breakdown = {
        "query_rewrite_score": 0.0,
        "table_score": 0.0,
        "dimension_score": 0.0,
        "measure_score": 0.0,
        "join_score": 0.0,
        "sql_structure_score": 0.0,
        "validation_score": 0.0,
        "hallucination_penalty": 0.0,
        "complexity_penalty": 0.0
    }

    recommendations = []

    sql_lower = sql.lower()

    if rewritten and len(
        rewritten.split()
    ) >= 5:

        breakdown[
            "query_rewrite_score"
        ] = 0.15

        score += 0.15

    else:

        recommendations.append(
            "Improve semantic query rewriting."
        )

    if tables:

        breakdown[
            "table_score"
        ] = 0.15

        score += 0.15

    else:

        recommendations.append(
            "No relevant tables selected."
        )

    if dimensions:

        breakdown[
            "dimension_score"
        ] = 0.15

        score += 0.15

    else:

        recommendations.append(
            "No relevant dimensions selected."
        )

    if measures:

        breakdown[
            "measure_score"
        ] = 0.15

        score += 0.15

    else:

        recommendations.append(
            "No relevant measures selected."
        )

    if joins:

        breakdown[
            "join_score"
        ] = 0.10

        score += 0.10

    if sql_lower.startswith(
        "select"
    ):

        breakdown[
            "sql_structure_score"
        ] += 0.10

        score += 0.10

    if "group by" in sql_lower:

        breakdown[
            "sql_structure_score"
        ] += 0.05

        score += 0.05

    if "order by" in sql_lower:

        breakdown[
            "sql_structure_score"
        ] += 0.05

        score += 0.05

    if validation.get(
        "valid",
        True
    ):

        breakdown[
            "validation_score"
        ] = 0.10

        score += 0.10

    else:

        score -= 0.10

        recommendations.append(
            "SQL validation failed."
        )

    hallucinated_terms = [
        "factsales",
        "branchdim",
        "datedim",
        "salesdim",
        "customerdim",
        "productdim",
        "unknown_table",
        "unknown_column"
    ]

    hallucination_found = any(
        term in sql_lower
        for term in hallucinated_terms
    )

    if hallucination_found:

        breakdown[
            "hallucination_penalty"
        ] = -0.25

        score -= 0.25

        recommendations.append(
            "Hallucinated schema detected."
        )

    nested_selects = len(
        re.findall(
            r"\bselect\b",
            sql_lower
        )
    )

    if nested_selects > 4:

        penalty = min(
            0.10,
            nested_selects * 0.02
        )

        breakdown[
            "complexity_penalty"
        ] -= penalty

        score -= penalty

        recommendations.append(
            "SQL query overly complex."
        )

    complexity = 0

    complexity += len(
        re.findall(
            r"\bjoin\b",
            sql_lower
        )
    )

    complexity += len(
        re.findall(
            r"\bcase\b",
            sql_lower
        )
    )

    complexity += len(
        re.findall(
            r"\bgroup by\b",
            sql_lower
        )
    )

    complexity += len(
        re.findall(
            r"\bover\b",
            sql_lower
        )
    )

    score = max(
        0.0,
        min(1.0, score)
    )

    if score >= 0.90:
        quality = "Excellent"

    elif score >= 0.75:
        quality = "High"

    elif score >= 0.60:
        quality = "Moderate"

    elif score >= 0.40:
        quality = "Low"

    else:
        quality = "Poor"

    return {
        "model_provider": provider,

        "user_query": user_query,

        "confidence": round(
            score,
            2
        ),

        "quality": quality,

        "breakdown": {
            k: round(v, 2)
            for k, v in breakdown.items()
        },

        "tables": tables,

        "dimensions": dimensions,

        "measures": measures,

        "joins": joins,

        "retrieval_count": len(
            retrieved_rows
        ),

        "rewritten_query": rewritten,

        "sql_length": len(
            sql
        ),

        "complexity_score": complexity,

        "hallucination_detected": hallucination_found,

        "validation": validation,

        "recommendations": recommendations if recommendations else [
            "Pipeline performing optimally."
        ]
    }
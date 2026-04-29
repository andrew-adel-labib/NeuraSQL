import re
from typing import Dict, Optional


def evaluate_pipeline(
    user_query: str,
    rewritten: str,
    semantic_plan: Dict,
    dax: str,
    validation: Optional[Dict] = None,
    retrieved_rows: Optional[list] = None,
    tables: Optional[list] = None,
    dimensions: Optional[list] = None,
    measures: Optional[list] = None,
    relationships: Optional[list] = None,
    provider: str = "claude"
):
    """
    Full enterprise evaluation layer

    Supports:
    - Claude
    - OpenAI
    - Groq

    Evaluates:
    - Query rewriting quality
    - Table relevance
    - Dimension relevance
    - Measure relevance
    - Relationship relevance
    - DAX structural validity
    - Validation quality
    - Hallucination risk
    - DAX complexity
    - Confidence scoring
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

    relationships = relationships or semantic_plan.get(
        "relationships",
        []
    )

    score = 0.0

    breakdown = {
        "query_rewrite_score": 0.0,
        "table_score": 0.0,
        "dimension_score": 0.0,
        "measure_score": 0.0,
        "relationship_score": 0.0,
        "dax_structure_score": 0.0,
        "validation_score": 0.0,
        "hallucination_penalty": 0.0,
        "complexity_penalty": 0.0
    }

    recommendations = []

    dax_lower = dax.lower()

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

        if len(tables) > 10:
            recommendations.append(
                "Too many tables selected; improve schema precision."
            )

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

    if relationships:

        breakdown[
            "relationship_score"
        ] = 0.10

        score += 0.10

    else:
        recommendations.append(
            "Relationship planning weak."
        )

    dax_score = 0.0

    if dax_lower.startswith(
        "evaluate"
    ):
        dax_score += 0.05

    if "summarizecolumns" in dax_lower:
        dax_score += 0.05

    if "filter(" in dax_lower:
        dax_score += 0.05

    if re.search(
        r'"metric"|sales revenue|sales volume',
        dax,
        re.IGNORECASE
    ):
        dax_score += 0.05

    breakdown[
        "dax_structure_score"
    ] = dax_score

    score += dax_score

    if dax_score < 0.15:
        recommendations.append(
            "Generated DAX structure is weak."
        )

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
            "DAX validation failed; syntax or semantic issues detected."
        )

    hallucinated_terms = [
        "branchdim",
        "salesdim",
        "datedimensions",
        "'date'",
        "'sales'",
        "factsales",
        "customerdim",
        "productdim",
        "unknown_table",
        "unknown_measure"
    ]

    hallucination_found = any(
        term in dax_lower
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

    nested_filters = len(
        re.findall(
            r"\bfilter\s*\(",
            dax_lower
        )
    )

    if nested_filters > 3:

        penalty = min(
            0.10,
            nested_filters * 0.02
        )

        breakdown[
            "complexity_penalty"
        ] -= penalty

        score -= penalty

        recommendations.append(
            "Too many nested FILTER statements."
        )

    complexity = 0

    complexity += len(
        re.findall(
            r"\bcalculate\b",
            dax_lower
        )
    )

    complexity += len(
        re.findall(
            r"\bvar\b",
            dax_lower
        )
    )

    complexity += len(
        re.findall(
            r"\breturn\b",
            dax_lower
        )
    )

    complexity += len(
        re.findall(
            r"\baddcolumns\b",
            dax_lower
        )
    )

    complexity += nested_filters

    if complexity > 4:

        penalty = min(
            0.15,
            complexity * 0.03
        )

        breakdown[
            "complexity_penalty"
        ] -= penalty

        score -= penalty

        recommendations.append(
            "DAX overly complex; simplify."
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

        "relationships": relationships,

        "retrieval_count": len(
            retrieved_rows
        ),

        "rewritten_query": rewritten,

        "dax_length": len(
            dax
        ),

        "complexity_score": complexity,

        "nested_filter_count": nested_filters,

        "hallucination_detected": hallucination_found,

        "validation": validation,

        "recommendations": recommendations if recommendations else [
            "Pipeline performing optimally."
        ]
    }
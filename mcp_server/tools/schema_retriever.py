import re
import numpy as np
from sentence_transformers import SentenceTransformer



embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)



BUSINESS_ALIASES = {
    "branch": [
        "branch",
        "store",
        "location",
        "city",
        "region",
        "district",
        "area"
    ],

    "sales": [
        "sales",
        "revenue",
        "income",
        "orders",
        "profit",
        "margin"
    ],

    "customer": [
        "customer",
        "client",
        "buyer",
        "customer channel",
        "segment"
    ],

    "date": [
        "date",
        "year",
        "month",
        "quarter",
        "week",
        "time",
        "trend"
    ],

    "product": [
        "product",
        "item",
        "sku",
        "category",
        "brand",
        "hierarchy"
    ],

    "salesman": [
        "salesman",
        "sales rep",
        "representative",
        "seller"
    ],

    "geography": [
        "region",
        "district",
        "city",
        "area",
        "geography"
    ]
}



def embed(text: str):
    return embedding_model.encode(text)



def cosine(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )



def normalize_query(question: str) -> str:
    q = question.lower()

    expanded_terms = []

    for canonical, aliases in BUSINESS_ALIASES.items():
        if any(alias in q for alias in aliases):
            expanded_terms.append(canonical)

    return f"{question} {' '.join(expanded_terms)}"



def build_table_text(table: dict) -> str:
    table_name = table.get("name", "")

    columns = " ".join(
        table.get("columns", [])
    )

    aliases = []

    lower_name = table_name.lower()

    for canonical, alias_list in BUSINESS_ALIASES.items():
        if canonical in lower_name:
            aliases.extend(alias_list)

    for col in table.get("columns", []):
        col_lower = col.lower()

        for canonical, alias_list in BUSINESS_ALIASES.items():
            if any(alias in col_lower for alias in alias_list):
                aliases.extend(alias_list)

    alias_text = " ".join(
        list(set(aliases))
    )

    return f"""
TABLE: {table_name}
COLUMNS: {columns}
BUSINESS_TERMS: {alias_text}
"""



def build_schema_index(schema: dict):
    tables = schema.get("tables", [])

    index = []

    for table in tables:
        text = build_table_text(
            table
        )

        index.append({
            "table": table,
            "text": text,
            "embedding": embed(text)
        })

    return index



def heuristic_boost(
    question: str,
    table: dict
) -> float:

    boost = 0.0

    q = question.lower()

    table_name = table.get(
        "name",
        ""
    ).lower()

    columns = " ".join(
        table.get("columns", [])
    ).lower()

    if any(x in q for x in [
        "branch",
        "city",
        "district",
        "region",
        "area",
        "location"
    ]):
        if any(x in table_name or x in columns for x in [
            "branch",
            "city",
            "district",
            "region",
            "area"
        ]):
            boost += 0.25

    if any(x in q for x in [
        "year",
        "month",
        "quarter",
        "trend",
        "date",
        "time"
    ]):
        if any(x in table_name or x in columns for x in [
            "date",
            "year",
            "month",
            "quarter"
        ]):
            boost += 0.25

    if any(x in q for x in [
        "sales",
        "revenue",
        "profit",
        "margin"
    ]):
        if any(x in table_name or x in columns for x in [
            "sales",
            "revenue",
            "profit"
        ]):
            boost += 0.25

    if "customer" in q:
        if "customer" in table_name or "customer" in columns:
            boost += 0.20

    if any(x in q for x in [
        "product",
        "item",
        "sku",
        "brand"
    ]):
        if any(x in table_name or x in columns for x in [
            "product",
            "item",
            "sku",
            "brand"
        ]):
            boost += 0.20

    if "salesman" in q:
        if "salesman" in table_name or "salesman" in columns:
            boost += 0.20

    return boost



def retrieve_relevant_tables(
    question: str,
    index,
    top_k=8
):
    normalized_query = normalize_query(
        question
    )

    q_emb = embed(
        normalized_query
    )

    scored = []

    for item in index:
        semantic_score = cosine(
            q_emb,
            item["embedding"]
        )

        boost = heuristic_boost(
            normalized_query,
            item["table"]
        )

        final_score = (
            semantic_score + boost
        )

        scored.append({
            "score": final_score,
            "semantic_score": semantic_score,
            "boost": boost,
            "table": item["table"]
        })

    scored = sorted(
        scored,
        key=lambda x: x["score"],
        reverse=True
    )

    return [
        x["table"]
        for x in scored[:top_k]
    ]



def retrieve_with_scores(
    question: str,
    index,
    top_k=8
):
    normalized_query = normalize_query(
        question
    )

    q_emb = embed(
        normalized_query
    )

    scored = []

    for item in index:
        semantic_score = cosine(
            q_emb,
            item["embedding"]
        )

        boost = heuristic_boost(
            normalized_query,
            item["table"]
        )

        final_score = (
            semantic_score + boost
        )

        scored.append({
            "table": item["table"]["name"],
            "score": round(
                final_score,
                4
            ),
            "semantic_score": round(
                semantic_score,
                4
            ),
            "boost": round(
                boost,
                4
            )
        })

    scored = sorted(
        scored,
        key=lambda x: x["score"],
        reverse=True
    )

    return scored[:top_k]



def retrieve_full_semantic_context(
    model: dict
):
    context = []

    context.append("TABLES:")
    for t in model.get(
        "tables",
        []
    ):
        context.append(
            f"{t['name']}: {', '.join(t['columns'])}"
        )

    context.append(
        "\nRELATIONSHIPS:"
    )

    for r in model.get(
        "relationships",
        []
    ):
        context.append(str(r))

    context.append(
        "\nMEASURES:"
    )

    for m in model.get(
        "measures",
        []
    ):
        measure_expression = m.get(
            "expression",
            ""
        )

        context.append(
            f"{m['name']}: {measure_expression}"
        )

    return "\n".join(context)
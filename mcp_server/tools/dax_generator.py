import os
import re
import json

from backend.app.llm.client import chat
from backend.app.exceptions import PlanningError
from mcp_server.policies.dax_rules import DAX_SYSTEM_PROMPT

from mcp_server.tools.schema_cache import (
    load_cached_query,
    save_cached_query
)

from mcp_server.tools.schema_retriever import (
    build_schema_index,
    retrieve_relevant_tables
)

from mcp_server.tools.query_rewriter import (
    rewrite_query,
    extract_query_intent
)

from mcp_server.tools.reranker import (
    extract_ranked_components
)

from mcp_server.tools.dimension_selector import (
    select_dimensions
)

from mcp_server.tools.evaluation import (
    evaluate_pipeline
)

from mcp_server.tools.dax_validator import (
    validate_dax
)

from mcp_server.tools.business_dimension_mapper import (
    correct_user_dimension_filters
)


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SCHEMA_PATH = os.path.join(
    BASE_DIR,
    "../../semantic_model.json"
)


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


def build_context(
    ranked_schema,
    model
):
    context = []

    context.append("RANKED TABLES:")

    for t in ranked_schema.get("tables", []):
        context.append(
            f"- Rank {t['rank']}: {t['name']} ({t.get('reason', '')})"
        )

    context.append("\nTABLE COLUMNS:")

    for ranked_table in ranked_schema.get("tables", []):
        table_name = ranked_table["name"]

        for table in model.get("tables", []):
            if table["name"] == table_name:
                context.append(
                    f"{table['name']}: {', '.join(table['columns'])}"
                )

    context.append("\nRANKED DIMENSIONS:")

    for d in ranked_schema.get("dimensions", []):
        context.append(
            f"- Rank {d['rank']}: {d['table']}[{d['column']}] ({d.get('reason', '')})"
        )

    context.append("\nRANKED MEASURES:")

    for m in ranked_schema.get("measures", []):
        context.append(
            f"- Rank {m['rank']}: {m['name']} ({m.get('reason', '')})"
        )

    context.append("\nRANKED RELATIONSHIPS:")

    for r in ranked_schema.get("relationships", []):
        context.append(
            f"- Rank {r['rank']}: {r['name']} ({r.get('reason', '')})"
        )

    context.append("\nIMPORTANT RULES:")

    context.extend([
        "- ONLY use ranked schema above",
        "- NEVER invent tables",
        "- NEVER invent dimensions",
        "- NEVER invent measures",
        "- NEVER invent relationships",
        "- ALWAYS prioritize higher ranked components",
        "- Prefer measures over raw aggregation",
        "- Use DateDim for time intelligence",
        "- Use branch dimensions for location filtering",
        "- Use SUMMARIZECOLUMNS",
        "- Keep DAX executable"
    ])

    return "\n".join(context)


def clean_dax(
    dax: str
) -> str:

    dax = dax.strip()

    if dax.startswith("```"):
        dax = dax.replace(
            "```dax",
            ""
        )

        dax = dax.replace(
            "```",
            ""
        )

    if dax.count("(") > dax.count(")"):
        dax += "\n)"

    return dax.strip()


def fix_dax_common_errors(
    dax: str,
    model: dict
) -> str:

    def get_branch_column():
        for t in model.get("tables", []):
            if t["name"] == "QBS_SighCast_Branch":
                for col in t["columns"]:
                    if "branch_name" in col.lower():
                        return col

        return "Branch_Name"

    branch_col = get_branch_column()

    dax = re.sub(
        r"'QBS_SighCast_Branch'\[(.*?)\]\s*=\s*\"(.*?)\"",
        lambda m: f"""FILTER(
        ALL('QBS_SighCast_Branch'),
        'QBS_SighCast_Branch'[{branch_col}] = "{m.group(2).title()}"
    )""",
        dax
    )

    dax = re.sub(
        r"'QBS_SighCast_Sales'\[Branch\]\s*=\s*\"(.*?)\"",
        lambda m: f"""FILTER(
        ALL('QBS_SighCast_Branch'),
        'QBS_SighCast_Branch'[{branch_col}] = "{m.group(1).title()}"
    )""",
        dax
    )

    dax = re.sub(
        r"FILTER\(\s*ALL\('DateDim'\),\s*FILTER\(\s*ALL\('DateDim'\),(.*?)\)\s*\)",
        r"FILTER(ALL('DateDim'), \1)",
        dax,
        flags=re.DOTALL
    )

    dax = re.sub(
        r"FILTER\(\s*ALL\('QBS_SighCast_Branch'\),\s*FILTER\(\s*ALL\('QBS_SighCast_Branch'\),(.*?)\)\s*\)",
        r"FILTER(ALL('QBS_SighCast_Branch'), \1)",
        dax,
        flags=re.DOTALL
    )

    dax = re.sub(
        r'="(.*?)"',
        lambda m: f'="{m.group(1).title()}"',
        dax
    )

    return dax


def generate_dax(
    question: str,
    model_provider: str = "claude"
):
    """
    Full enterprise DAX generation pipeline
    Supports:
    - Claude
    - OpenAI
    - Groq
    """

    cache_key = (
        f"full_pipeline::{model_provider}::{question}"
    )

    cached = load_cached_query(cache_key)

    if cached:
        return cached

    model = load_semantic_model()

    if not model:
        raise PlanningError(
            "Semantic model failed to load"
        )

    rewritten_query = rewrite_query(
        question,
        model_provider=model_provider
    )

    query_intent = extract_query_intent(
        rewritten_query,
        model_provider=model_provider
    )

    index = build_schema_index(model)

    retrieve_relevant_tables(
        rewritten_query,
        index,
        top_k=10
    )

    ranked_schema = extract_ranked_components(
        rewritten_query,
        model,
        model_provider=model_provider
    )

    semantic_context = build_context(
        ranked_schema,
        model
    )

    dimension_plan = select_dimensions(
        rewritten_query,
        semantic_context,
        model_provider=model_provider
    )

    dimension_plan["filters"] = (
        correct_user_dimension_filters(
            dimension_plan.get(
                "filters",
                {}
            )
        )
    )

    prompt = f"""
{DAX_SYSTEM_PROMPT}

====================================================
SEMANTIC CONTEXT (STRICT USAGE)
====================================================

{semantic_context}

====================================================
QUERY INTENT
====================================================

{json.dumps(query_intent, indent=2)}

====================================================
DIMENSION PLAN
====================================================

{json.dumps(dimension_plan, indent=2)}

====================================================
IMPORTANT RULES
====================================================

- ONLY use ranked schema
- NEVER invent tables
- NEVER invent dimensions
- NEVER invent measures
- NEVER invent relationships
- ALWAYS prioritize ranked components
- Use SUMMARIZECOLUMNS
- Use FILTER for time and branch filters
- Prefer standardized "Metric"
- Keep DAX simple
- Avoid VAR unless essential
- Avoid CALCULATE unless essential

====================================================
USER QUESTION
====================================================

Original Question:
{question}

Rewritten Question:
{rewritten_query}

====================================================
OUTPUT
====================================================

Return ONLY valid executable DAX query.
"""

    raw_dax = chat(
        prompt=rewritten_query,
        system_prompt=prompt,
        provider=model_provider
    )

    dax = clean_dax(raw_dax)

    dax = fix_dax_common_errors(
        dax,
        model
    )

    validation = {
        "valid": True,
        "errors": []
    }

    try:
        validate_dax(dax)

    except Exception as e:
        validation = {
            "valid": False,
            "errors": [str(e)]
        }

    evaluation = evaluate_pipeline(
        user_query=question,
        rewritten=rewritten_query,
        semantic_plan=ranked_schema,
        dax=dax,
        validation=validation,
        retrieved_rows=[],
        tables=ranked_schema.get("tables", []),
        dimensions=dimension_plan.get("dimensions", []),
        measures=ranked_schema.get("measures", []),
        relationships=ranked_schema.get("relationships", []),
        provider=model_provider
    )

    result = {
        "dax": dax,
        "model_provider": model_provider,
        "evaluation": evaluation,
        "validation": validation,
        "rewritten_query": rewritten_query,
        "query_intent": query_intent,
        "ranked_schema": ranked_schema,
        "tables_used": [
            t["name"]
            for t in ranked_schema.get(
                "tables",
                []
            )
        ],
        "dimension_plan": dimension_plan
    }

    save_cached_query(
        cache_key,
        result
    )

    return result
import os
import requests
import msal
import traceback
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from datetime import datetime
from decimal import Decimal

from mcp_server.tools.dax_generator import (
    generate_dax
)

from mcp_server.tools.dax_executor import (
    execute_dax
)

from mcp_server.tools.answer_summarizer import (
    summarize_answer
)

from mcp_server.tools.llm_judge import (
    judge_pipeline
)


load_dotenv()

app = FastAPI(
    title="AI BI Copilot"
)


TENANT_ID = os.getenv("PBI_TENANT_ID")
CLIENT_ID = os.getenv("PBI_CLIENT_ID")
CLIENT_SECRET = os.getenv("PBI_CLIENT_SECRET")
WORKSPACE_ID = os.getenv("PBI_WORKSPACE_ID")
REPORT_ID = os.getenv("PBI_REPORT_ID")
DATASET_ID = os.getenv("PBI_DATASET_ID")

AUTHORITY = (
    f"https://login.microsoftonline.com/{TENANT_ID}"
)

SCOPE = [
    "https://analysis.windows.net/powerbi/api/.default"
]


def get_access_token():
    msal_app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    result = msal_app.acquire_token_for_client(
        scopes=SCOPE
    )

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"]


def generate_embed_token():
    try:
        access_token = get_access_token()

        url = (
            f"https://api.powerbi.com/v1.0/myorg/groups/"
            f"{WORKSPACE_ID}/reports/{REPORT_ID}/GenerateToken"
        )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        body = {
            "accessLevel": "View",
            "datasets": [
                {"id": DATASET_ID}
            ],
            "reports": [
                {"id": REPORT_ID}
            ]
        }

        res = requests.post(
            url,
            headers=headers,
            json=body
        )

        if res.status_code != 200:
            return None

        return res.json().get("token")

    except Exception:
        return None


def extract_filters(question: str):
    filters = []

    q = question.lower()

    if "last year" in q:
        filters.append({
            "$schema": "http://powerbi.com/product/schema#basic",
            "target": {
                "table": "Date",
                "column": "Year"
            },
            "operator": "In",
            "values": [2025]
        })

    if "this year" in q:
        filters.append({
            "$schema": "http://powerbi.com/product/schema#basic",
            "target": {
                "table": "Date",
                "column": "Year"
            },
            "operator": "In",
            "values": [2026]
        })

    if "january" in q:
        filters.append({
            "$schema": "http://powerbi.com/product/schema#basic",
            "target": {
                "table": "Date",
                "column": "Month"
            },
            "operator": "In",
            "values": [1]
        })

    return filters


def normalize_value(v):
    if isinstance(v, datetime):
        return v.isoformat()

    if isinstance(v, Decimal):
        return float(v)

    if "DateTime" in str(type(v)):
        try:
            return str(v)
        except:
            return None

    return v


def normalize_rows(rows):
    return [
        [
            normalize_value(cell)
            for cell in row
        ]
        for row in rows
    ]


@app.post("/ask")
async def ask(request: dict):

    question = request.get("question")

    model_provider = request.get(
        "model_provider",
        "claude"
    )

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question required"
        )

    try:

        dax_result = generate_dax(
            question=question,
            model_provider=model_provider
        )

        dax = dax_result["dax"]

        validation = dax_result.get(
            "validation",
            {
                "valid": True,
                "errors": []
            }
        )

        execution_error = None

        try:
            if validation["valid"]:
                rows, cols = execute_dax(dax)
            else:
                rows, cols = [], []

        except Exception as exec_error:
            rows, cols = [], []
            execution_error = str(exec_error)

        rows = normalize_rows(rows)

        df = pd.DataFrame(
            rows,
            columns=cols
        )

        summary = summarize_answer(
            question=question,
            rows=df.to_dict(
                orient="records"
            ),
            model_provider=model_provider
        )

        llm_judge = judge_pipeline(
            user_query=question,
            rewritten_query=dax_result[
                "rewritten_query"
            ],
            semantic_plan=dax_result[
                "ranked_schema"
            ],
            dax=dax,
            retrieved_rows=df.to_dict(
                orient="records"
            ),
            summary=summary,
            model_provider=model_provider
        )

        embed_token = generate_embed_token()

        embed_url = (
            f"https://app.powerbi.com/reportEmbed?"
            f"reportId={REPORT_ID}&groupId={WORKSPACE_ID}"
        )

        filters = extract_filters(question)

        return {
            "mode": "powerbi_embedded",

            "model_provider": model_provider,

            "question": question,

            "rewritten_query": dax_result[
                "rewritten_query"
            ],

            "query_intent": dax_result[
                "query_intent"
            ],

            "semantic_plan": dax_result[
                "ranked_schema"
            ],

            "dimension_plan": dax_result[
                "dimension_plan"
            ],

            "dax": dax,

            "validation": validation,

            "execution_error": execution_error,

            "rows": df.to_dict(
                orient="records"
            ),

            "columns": cols,

            "summary": summary,

            "evaluation": dax_result[
                "evaluation"
            ],

            "llm_judge": llm_judge,

            "powerbi": {
                "embedUrl": embed_url,
                "accessToken": embed_token,
                "filters": filters
            } if embed_token and validation["valid"] and not execution_error else None
        }

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
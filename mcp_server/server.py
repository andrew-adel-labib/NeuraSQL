import pandas as pd

from fastapi import FastAPI
from fastapi import HTTPException

from mcp_server.tools.sql_generator import (
    generate_sql
)

from mcp_server.tools.sql_validator import (
    validate
)

from mcp_server.tools.sql_executer import (
    execute_sql
)

from mcp_server.tools.cache import (
    load_cache
)

from mcp_server.tools.nl_explainer import (
    explain
)

from mcp_server.tools.answer_summarizer import (
    summarize_answer
)

from mcp_server.tools.query_rewriter import (
    process_query
)

from mcp_server.tools.query_interpreter import (
    interpret
)

from mcp_server.tools.rag_semantic import (
    retrieve_context
)

from mcp_server.tools.semantic_planner import (
    plan_semantics
)

from mcp_server.tools.dimension_selector import (
    select_dimensions
)

from mcp_server.tools.evaluation import (
    evaluate_pipeline
)

from mcp_server.tools.llm_judge import (
    judge_pipeline
)


app = FastAPI(
    title="Enterprise AI SQL Analytics Copilot"
)


@app.on_event("startup")
def startup_event():

    print("\n🚀 Loading ERP database cache...\n")

    load_cache()

    print("\n✅ ERP database cache loaded.\n")


@app.get("/")
async def root():

    return {
        "status": "running",
        "service": "Enterprise AI SQL Analytics Copilot"
    }


@app.post("/ask")
async def ask(request: dict):

    try:

        print("\n============================")
        print("🚀 NEW REQUEST RECEIVED")
        print("============================\n")

        print("STEP 1 - Reading Request")

        question = request.get("question")

        model_provider = request.get(
            "provider",
            "claude"
        )

        print(f"Question: {question}")
        print(f"Provider: {model_provider}")

        if not question:

            raise HTTPException(
                status_code=400,
                detail="Question is required."
            )

        print("\nSTEP 2 - Processing Query")

        query_processing = process_query(
            question,
            model_provider=model_provider
        )

        print("✅ Query Processing Completed")

        rewritten_query = query_processing.get(
            "rewritten_query",
            question
        )

        query_intent = query_processing.get(
            "intent",
            {}
        )

        print(f"Rewritten Query: {rewritten_query}")

        print("\nSTEP 3 - Retrieving Semantic Context")

        semantic_context = retrieve_context(
            rewritten_query
        )

        print("✅ Semantic Context Retrieved")

        print("\nSTEP 4 - Planning Semantics")

        semantic_plan = plan_semantics(
            rewritten_query,
            semantic_context,
            model_provider=model_provider
        )

        print("✅ Semantic Planning Completed")

        print("\nSTEP 5 - Selecting Dimensions")

        dimension_plan = select_dimensions(
            rewritten_query,
            semantic_context,
            model_provider=model_provider
        )

        print("✅ Dimension Selection Completed")

        print("\nSTEP 6 - Generating SQL")

        sql = generate_sql(
            rewritten_query
        )

        print("✅ SQL Generated")
        print(sql)

        print("\nSTEP 7 - Validating SQL")

        validate(sql)

        validation_result = {
            "valid": True
        }

        print("✅ SQL Validation Passed")

        print("\nSTEP 8 - Executing SQL")

        rows, cols = execute_sql(sql)

        print(f"✅ SQL Executed Successfully")
        print(f"Rows Returned: {len(rows)}")

        print("\nSTEP 9 - Creating DataFrame")

        df = pd.DataFrame(
            rows,
            columns=cols
        )

        print("✅ DataFrame Created")

        print("\nSTEP 10 - Generating Explanation")

        explanation = explain(
            question,
            rows,
            cols
        )

        print("✅ Explanation Generated")

        print("\nSTEP 11 - Summarizing Answer")

        summary = summarize_answer(
            question,
            rows,
            model_provider=model_provider
        )

        print("✅ Summary Generated")

        print("\nSTEP 12 - Evaluating Pipeline")

        evaluation = evaluate_pipeline(
            user_query=question,
            rewritten=rewritten_query,
            semantic_plan=semantic_plan,
            sql=sql,
            validation=validation_result,
            retrieved_rows=rows,
            tables=semantic_plan.get(
                "tables",
                []
            ),
            dimensions=semantic_plan.get(
                "dimensions",
                []
            ),
            measures=semantic_plan.get(
                "measures",
                []
            ),
            joins=semantic_plan.get(
                "joins",
                []
            ),
            provider=model_provider
        )

        print("✅ Pipeline Evaluation Completed")

        print("\nSTEP 13 - Running LLM Judge")

        qa_judge = judge_pipeline(
            user_query=question,
            rewritten_query=rewritten_query,
            semantic_plan=semantic_plan,
            sql=sql,
            retrieved_rows=rows,
            summary=summary,
            model_provider=model_provider
        )

        print("✅ LLM Judge Completed")

        print("\n🎉 REQUEST COMPLETED SUCCESSFULLY\n")

        return {

            "status": "success",

            "mode": "sql_analytics",

            "provider": model_provider,

            "question": question,

            "rewritten_query": rewritten_query,

            "query_intent": query_intent,

            "semantic_context": semantic_context,

            "semantic_plan": semantic_plan,

            "dimension_plan": dimension_plan,

            "sql": sql,

            "validation": validation_result,

            "columns": cols,

            "row_count": len(rows),

            "rows": rows,

            "dataframe": df.to_dict(
                orient="records"
            ),

            "explanation": explanation,

            "summary": summary,

            "evaluation": evaluation,

            "qa_judge": qa_judge
        }

    except HTTPException:

        raise

    except Exception as e:

        print("\n❌ ERROR OCCURRED")
        print(str(e))
        print(type(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

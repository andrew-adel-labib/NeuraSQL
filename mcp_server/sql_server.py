# import pandas as pd

# from fastapi import FastAPI, HTTPException
# from mcp_server.tools.sql_generator import generate_sql
# from mcp_server.tools.sql_validator import validate
# from mcp_server.tools.sql_executer import execute_sql
# from mcp_server.tools.cache import get_cache, load_cache
# from mcp_server.tools.query_interpreter import interpret
# from mcp_server.tools.feature_engineering import build_time_series
# from mcp_server.tools.predictor import predict as run_prediction
# from mcp_server.tools.nl_explainer import explain, explain_forecast


# app = FastAPI(title="AI SQL and Forecast MCP Server")


# @app.on_event("startup")
# def startup_event():
#     print("🚀 Loading database into memory...")
#     load_cache()
#     print("Database cache loaded successfully.")


# @app.post("/ask")
# async def ask(request: dict):

#     question = request.get("question")

#     if not question:
#         raise HTTPException(status_code=400, detail="Question is required.")

#     try:
#         sql = generate_sql(question)
#         validate(sql)

#         rows, cols = execute_sql(sql)

#         answer = explain(question, rows, cols)

#         return {
#             "mode": "ask",
#             "sql": sql,
#             "answer": answer,
#             "rows": rows
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/predict")
# async def predict(request: dict):

#     question = request.get("question")

#     if not question:
#         raise HTTPException(status_code=400, detail="Question is required.")

#     try:
#         config = interpret(question)

#         db = get_cache()

#         table = config.get("target_table")

#         if table not in db:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Table '{table}' not found in cached database."
#             )

#         df = db[table]

#         series = build_time_series(
#             df,
#             config.get("date_column"),
#             config.get("target_column"),
#             config.get("aggregation", "sum")
#         )

#         if series.empty:
#             raise HTTPException(
#                 status_code=400,
#                 detail="No data available after aggregation."
#             )

#         horizon = config.get("horizon_months", 3)

#         final_preds = run_prediction(series, horizon)

#         last_date = pd.to_datetime(series.index[-1])

#         future_index = pd.date_range(
#             start=last_date,
#             periods=horizon + 1,
#             freq="M"
#         )[1:]

#         forecast_df = pd.DataFrame({
#             "Date": future_index,
#             "Forecast": final_preds
#         })

#         explanation = explain_forecast(question, forecast_df)

#         return {
#             "mode": "predict",
#             "forecast": forecast_df.to_dict(orient="records"),
#             "explanation": explanation
#         }

#     except HTTPException:
#         raise

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


import pandas as pd
from fastapi import FastAPI, HTTPException

from mcp_server.tools.sql_generator import generate_sql
from mcp_server.tools.sql_validator import validate
from mcp_server.tools.sql_executer import execute_sql
from mcp_server.tools.cache import get_cache, load_cache
from mcp_server.tools.query_interpreter import interpret
from mcp_server.tools.feature_engineering import build_time_series
from mcp_server.tools.predictor import predict as run_prediction
from mcp_server.tools.nl_explainer import explain, explain_forecast


app = FastAPI(title="AI SQL and Forecast MCP Server")


@app.on_event("startup")
def startup_event():
    print("🚀 Loading database into memory...")
    load_cache()
    print("Database cache loaded successfully.")


@app.post("/ask")
async def ask(request: dict):

    question = request.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")

    try:
        sql = generate_sql(question)
        validate(sql)

        rows, cols = execute_sql(sql)

        df = pd.DataFrame(rows, columns=cols)

        answer = explain(question, rows, cols)

        return {
            "mode": "ask",
            "sql": sql,
            "answer": answer,
            "columns": cols,
            "rows": rows,
            "dataframe": df.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
async def predict(request: dict):

    question = request.get("question")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")

    try:
        config = interpret(question)

        db = get_cache()

        table = config.get("target_table")

        if table not in db:
            raise HTTPException(
                status_code=400,
                detail=f"Table '{table}' not found."
            )

        df = db[table]

        series = build_time_series(
            df,
            config.get("date_column"),
            config.get("target_column"),
            config.get("aggregation", "sum")
        )

        if series.empty:
            raise HTTPException(
                status_code=400,
                detail="No data available."
            )

        horizon = config.get("horizon_months", 3)

        final_preds = run_prediction(series, horizon)

        last_date = pd.to_datetime(series.index[-1])

        future_index = pd.date_range(
            start=last_date,
            periods=horizon + 1,
            freq="M"
        )[1:]

        forecast_df = pd.DataFrame({
            "Date": future_index,
            "Forecast": final_preds
        })

        explanation = explain_forecast(question, forecast_df)

        return {
            "mode": "predict",
            "forecast": forecast_df.to_dict(orient="records"),
            "explanation": explanation
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
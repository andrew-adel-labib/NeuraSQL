from backend.app.llm.groq_client import chat
from backend.app.logging_config import setup_logger
from backend.app.exceptions import PlanningError

logger = setup_logger("planner")


def build_forecast_plan(question: str) -> dict:
    logger.info("Building forecast plan")

    try:
        _ = chat(question)
    except Exception as e:
        raise PlanningError(
            message="LLM planning failed",
            context={"question": question},
            cause=e,
        )

    return {
        "metric": "revenue",
        "time_grain": "daily",
        "history_days": 180,
        "models": ["ARIMA", "XGBOOST"],
        "features": ["lag_7", "rolling_14"],
    }
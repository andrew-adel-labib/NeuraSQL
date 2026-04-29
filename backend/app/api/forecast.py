from fastapi import APIRouter
from backend.app.security.intent_guard import classify_intent
from backend.app.llm.planner import build_forecast_plan

router = APIRouter()

@router.post("/")
def forecast(question: str):
    classify_intent(question)
    return build_forecast_plan(question)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.app.api.forecast import router
from backend.app.exceptions import ForecastingError
from backend.app.logging_config import setup_logger

logger = setup_logger("backend")

app = FastAPI(title="Forecasting API")
app.include_router(router, prefix="/forecast")

@app.exception_handler(ForecastingError)
async def handle_app_error(req: Request, exc: ForecastingError):
    logger.error(str(exc), exc_info=exc.cause)
    return JSONResponse(status_code=400, content=exc.to_dict())
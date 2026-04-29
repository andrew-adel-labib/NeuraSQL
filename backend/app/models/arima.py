from statsmodels.tsa.arima.model import ARIMA
from backend.app.exceptions import ModelExecutionError


def run_arima(series):
    try:
        return ARIMA(series, order=(2, 1, 2)).fit().forecast(30)
    except Exception as e:
        raise ModelExecutionError(
            message="ARIMA forecast failed",
            context={"order": "(2,1,2)", "horizon": 30},
            cause=e,
        )
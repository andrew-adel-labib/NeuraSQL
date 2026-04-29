from mcp_server.tools.arima_model import run_arima
from mcp_server.tools.xgboost_model import run_xgboost
from mcp_server.tools.lstm_model import run_lstm
from mcp_server.tools.ensemble import ensemble_predictions


def predict(series, steps):
    """
    Run multiple forecasting models and return ensemble prediction.
    """

    predictions = []

    try:
        predictions.append(run_arima(series, steps))
    except Exception as e:
        print("ARIMA failed:", e)

    try:
        predictions.append(run_xgboost(series, steps))
    except Exception as e:
        print("XGBoost failed:", e)

    try:
        predictions.append(run_lstm(series, steps))
    except Exception as e:
        print("LSTM failed:", e)

    if not predictions:
        raise Exception("All forecasting models failed.")

    final_preds = ensemble_predictions(*predictions)

    return final_preds
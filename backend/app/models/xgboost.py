import xgboost as xgb
from backend.app.exceptions import ModelExecutionError


def run_xgb(X, y):
    try:
        model = xgb.XGBRegressor()
        model.fit(X, y)
        return model.predict(X.tail(30))
    except Exception as e:
        raise ModelExecutionError(
            message="XGBoost forecast failed",
            context={"model": "XGBoost"},
            cause=e,
        )
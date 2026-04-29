import xgboost as xgb
import numpy as np


def run_xgboost(series, steps=3):

    values = series.values

    X = np.arange(len(values)).reshape(-1, 1)
    y = values

    model = xgb.XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3
    )

    model.fit(X, y)

    future = np.arange(len(values), len(values) + steps).reshape(-1, 1)
    preds = model.predict(future)

    return preds.tolist()
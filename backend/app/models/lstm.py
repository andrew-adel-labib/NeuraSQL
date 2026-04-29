import numpy as np
from typing import Tuple

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

from backend.app.exceptions import ModelExecutionError
from backend.app.logging_config import setup_logger

logger = setup_logger("lstm_model")


def _create_sequences(data: np.ndarray, window: int) -> Tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i : i + window])
        y.append(data[i + window])
    return np.array(X), np.array(y)


def run_lstm(
    series,
    horizon: int = 30,
    window: int = 14,
    epochs: int = 50,
) -> np.ndarray:
    """
    Train LSTM on a univariate time series and forecast future values.

    Parameters
    ----------
    series : pd.Series
        Historical time series
    horizon : int
        Forecast horizon
    window : int
        Lookback window
    epochs : int
        Training epochs
    """

    try:
        logger.info(
            "Running LSTM forecast",
            extra={
                "horizon": horizon,
                "window": window,
                "epochs": epochs,
            },
        )

        values = series.values.reshape(-1, 1)

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(values)

        X, y = _create_sequences(scaled, window)

        if len(X) == 0:
            raise ValueError("Not enough data for LSTM window size")

        X = X.reshape((X.shape[0], X.shape[1], 1))

        model = Sequential(
            [
                LSTM(64, activation="tanh", input_shape=(window, 1)),
                Dense(1),
            ]
        )

        model.compile(optimizer="adam", loss="mse")

        model.fit(
            X,
            y,
            epochs=epochs,
            batch_size=16,
            verbose=0,
            callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
        )

        # Recursive forecasting
        last_window = scaled[-window:].reshape((1, window, 1))
        preds = []

        for _ in range(horizon):
            next_val = model.predict(last_window, verbose=0)[0][0]
            preds.append(next_val)
            last_window = np.roll(last_window, -1, axis=1)
            last_window[0, -1, 0] = next_val

        preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
        return preds

    except Exception as e:
        logger.error("LSTM execution failed", exc_info=True)
        raise ModelExecutionError(
            message="LSTM forecast failed",
            context={
                "horizon": horizon,
                "window": window,
                "epochs": epochs,
            },
            cause=e,
        )
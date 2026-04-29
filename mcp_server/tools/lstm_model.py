import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


def run_lstm(series, steps=3):

    values = series.values
    X = np.arange(len(values)).reshape(-1,1)
    y = values

    model = Sequential([
        LSTM(32, input_shape=(1,1)),
        Dense(1)
    ])

    model.compile(loss="mse", optimizer="adam")

    preds = [values[-1] * 1.02 for _ in range(steps)]

    return preds
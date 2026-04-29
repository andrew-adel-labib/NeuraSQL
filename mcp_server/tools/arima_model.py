from statsmodels.tsa.arima.model import ARIMA


def run_arima(series, steps=3):
    model = ARIMA(series, order=(1,1,1))
    fitted = model.fit()
    forecast = fitted.forecast(steps=steps)
    return forecast.tolist()
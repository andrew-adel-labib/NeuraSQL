from backend.app.exceptions import ForecastingError


def build_features(df):
    if df.empty:
        raise ForecastingError(
            message="Feature build failed due to empty dataframe",
            context={"stage": "feature_engineering"},
        )

    df["lag_7"] = df["revenue"].shift(7)
    df["rolling_14"] = df["revenue"].rolling(14).mean()
    return df.dropna()
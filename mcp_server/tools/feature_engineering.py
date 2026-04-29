import pandas as pd


def build_time_series(df, date_column, target_column, aggregation="sum"):

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

    grouped = (
        df
        .groupby(pd.Grouper(key=date_column, freq="M"))[target_column]
    )

    if aggregation == "sum":
        series = grouped.sum()
    else:
        series = grouped.mean()

    return series.dropna()
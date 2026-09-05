"""
load_forecast_prophet.py
PERSON 2 — Load Forecasting Module (SECONDARY / seasonal cross-check model)

Prophet is good at capturing daily/weekly seasonality and gives a second
opinion next to the XGBoost forecast. Train and use it LOCALLY for your
model-comparison slide; see the deployment guide for why the live Streamlit
Cloud demo relies on XGBoost as the model actually served.

Run directly:  python ml/forecasting/load_forecast_prophet.py
"""

import pandas as pd
import joblib
from pathlib import Path
from prophet import Prophet


def train(
    csv_path="data/historical/full_dataset.csv", model_out="ml/models/prophet_load.pkl"
):
    df = pd.read_csv(csv_path)[["timestamp", "load_kw"]].rename(
        columns={"timestamp": "ds", "load_kw": "y"}
    )
    df["ds"] = pd.to_datetime(df["ds"])

    model = Prophet(
        daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False
    )
    model.fit(df)

    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_out)
    return model


def forecast_next_24h(model):
    future = model.make_future_dataframe(periods=24, freq="h")
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(24)


if __name__ == "__main__":
    m = train()
    print(forecast_next_24h(m))

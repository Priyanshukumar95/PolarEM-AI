"""PERSON 2 — Load Forecasting page."""

import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from ml.forecasting.load_forecast_xgboost import train as train_xgb, forecast_next_24h

st.header("🔋 Load Forecasting")
st.caption(
    "Person 2's module: XGBoost is the primary model served to the "
    "Optimization Engine. Prophet is available below as a second opinion."
)

DATA_PATH = Path("data/historical/full_dataset.csv")
MODEL_PATH = Path("ml/models/xgboost_load.pkl")

if not DATA_PATH.exists():
    st.warning("Generate the dataset on the Data Simulation page first.")
    st.stop()

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

if st.button("Train / retrain XGBoost model") or not MODEL_PATH.exists():
    with st.spinner("Training..."):
        model, metrics = train_xgb()
    st.success(
        f"Trained. MAPE: {metrics['mape']:.2f}% | RMSE: {metrics['rmse']:.2f} kW"
    )
else:
    model = joblib.load(MODEL_PATH)

forecast = forecast_next_24h(model, df)

st.subheader("Next 24-Hour Load Forecast (XGBoost — primary)")
st.line_chart(forecast.set_index("timestamp"))
st.dataframe(forecast, use_container_width=True)
st.download_button(
    "Download forecast (CSV)", forecast.to_csv(index=False), "load_forecast_24h.csv"
)

st.divider()
if st.checkbox("Also show Prophet cross-check (seasonal model, trains in ~2-3 sec)"):
    from ml.forecasting.load_forecast_prophet import (
        train as train_prophet,
        forecast_next_24h as prophet_forecast,
    )

    with st.spinner("Training Prophet..."):
        p_model = train_prophet()
        p_forecast = prophet_forecast(p_model).rename(
            columns={"ds": "timestamp", "yhat": "predicted_load_kw"}
        )
    st.subheader("Next 24-Hour Load Forecast (Prophet — seasonal cross-check)")
    st.line_chart(p_forecast.set_index("timestamp")[["predicted_load_kw"]])
    st.caption(
        "Compare the two curves — large disagreement between XGBoost and "
        "Prophet on a given hour is worth a second look before trusting "
        "the dispatch plan for that hour."
    )

"""PERSON 3 — Renewable Energy Forecasting page."""

import streamlit as st
from utils.style import apply_style
apply_style()
import pandas as pd
import joblib
from pathlib import Path
from ml.forecasting.renewable_forecast import (
    train_solar,
    train_wind,
    build_features,
    SOLAR_FEATURES,
    WIND_FEATURES,
)

st.header(" Renewable Energy Forecasting")
st.caption(" Solar & wind generation prediction.")

DATA_PATH = Path("data/historical/full_dataset.csv")
if not DATA_PATH.exists():
    st.warning("Generate the dataset on the Data Simulation page first.")
    st.stop()

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
solar_model_path = Path("ml/models/solar_model.pkl")
wind_model_path = Path("ml/models/wind_model.pkl")

c1, c2 = st.columns(2)
with c1:
    if st.button("Train solar model") or not solar_model_path.exists():
        with st.spinner("Training solar model..."):
            train_solar()
        st.success("Solar model trained.")
with c2:
    if st.button("Train wind model") or not wind_model_path.exists():
        with st.spinner("Training wind model..."):
            train_wind()
        st.success("Wind model trained.")

solar_model = joblib.load(solar_model_path)
wind_model = joblib.load(wind_model_path)

feat_df = build_features(df)
X_solar = feat_df[SOLAR_FEATURES].tail(24)
X_wind = feat_df[WIND_FEATURES].tail(24)

result = pd.DataFrame(
    {
        "timestamp": feat_df["timestamp"].tail(24).values,
        "predicted_solar_kw": solar_model.predict(X_solar).round(1),
        "predicted_wind_kw": wind_model.predict(X_wind).round(1),
    }
)

st.subheader("Next 24-Hour Renewable Generation Forecast")
st.line_chart(result.set_index("timestamp"))
st.dataframe(result, use_container_width=True)

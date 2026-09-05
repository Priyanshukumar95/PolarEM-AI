"""PERSON 4 — Anomaly Detection page."""

import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from ml.anomaly_detection.anomaly_detector import train, detect

st.header("🚨 Anomaly Detection & Predictive Maintenance")
st.caption(
    "Person 4's module: Isolation Forest flags equipment/sensor readings "
    "that look abnormal."
)

DATA_PATH = Path("data/historical/full_dataset.csv")
MODEL_PATH = Path("ml/models/anomaly_model.pkl")

if not DATA_PATH.exists():
    st.warning("Generate the dataset on the Data Simulation page first.")
    st.stop()

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

if st.button("Train anomaly detector") or not MODEL_PATH.exists():
    with st.spinner("Training Isolation Forest..."):
        model = train()
    st.success("Model trained.")
else:
    model = joblib.load(MODEL_PATH)

result = detect(model, df)
anomalies = result[result["is_anomaly"] == 1]

st.metric("Anomalies flagged (out of {} hours)".format(len(result)), len(anomalies))
st.line_chart(result.set_index("timestamp")[["load_kw"]])
st.subheader("Flagged anomalies")
st.dataframe(anomalies.tail(30), use_container_width=True)

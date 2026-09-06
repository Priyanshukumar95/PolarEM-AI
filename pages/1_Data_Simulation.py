"""PERSON 1 — Data Pipeline & Simulation page."""

import streamlit as st
from utils.style import apply_style
apply_style()
import pandas as pd
from pathlib import Path
from simulation.data_generator import main as generate_data

st.header("📊 Data Pipeline & Simulation")
st.caption("Person 1's module: synthetic sensor data generation and validation.")

days = st.slider("Days of hourly data to generate", 30, 180, 90)
if st.button("Regenerate synthetic data"):
    with st.spinner("Generating..."):
        df = generate_data(days=days)
    st.success(f"Generated {len(df)} hourly records.")

data_path = Path("data/historical/full_dataset.csv")
if data_path.exists():
    df = pd.read_csv(data_path, parse_dates=["timestamp"])
    st.write(
        f"Dataset: {len(df)} rows, {df['timestamp'].min()} to {df['timestamp'].max()}"
    )
    st.dataframe(df.tail(100), use_container_width=True)
    st.download_button(
        "Download full dataset (CSV)", df.to_csv(index=False), "full_dataset.csv"
    )
    st.markdown("**Temperature over time**")
    st.line_chart(df.set_index("timestamp")[["temperature_c"]])
else:
    st.info("No dataset yet — click the button above to generate one.")

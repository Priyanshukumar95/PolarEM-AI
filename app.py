"""
app.py
PERSON 5 — Dashboard / Integration Lead
Main entry point for the Streamlit app.

Run locally:   streamlit run app.py
Deploy:        push to GitHub, then deploy on share.streamlit.io
               with "app.py" as the main file path.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from simulation.data_generator import main as generate_data

st.set_page_config(
    page_title="Polar Energy Management System",
    page_icon="🧊",
    layout="wide",
)

st.title("🧊 AI-Driven Smart Energy Management System")
st.subheader("Polar Research Station — SIH Prototype Dashboard")

DATA_PATH = Path("data/historical/full_dataset.csv")

if not DATA_PATH.exists():
    with st.spinner("First run: generating 90 days of synthetic sensor data..."):
        generate_data()

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Load", f"{df['load_kw'].iloc[-1]:.0f} kW")
col2.metric("Solar Output", f"{df['solar_kw'].iloc[-1]:.0f} kW")
col3.metric("Wind Output", f"{df['wind_kw'].iloc[-1]:.0f} kW")
col4.metric("Battery SoC", f"{df['battery_soc_pct'].iloc[-1]:.0f}%")

st.markdown("### Last 7 days")
st.line_chart(
    df.set_index("timestamp")[["load_kw", "solar_kw", "wind_kw"]].tail(24 * 7)
)

st.markdown("""
Use the sidebar to open each module:

- **Data Simulation** — regenerate / inspect the synthetic sensor dataset
- **Load Forecasting** — XGBoost 24-hour demand prediction
- **Renewable Forecasting** — solar & wind generation prediction
- **Optimization Engine** — optimal dispatch across solar/wind/battery/
  generator (MILP)
- **Anomaly Detection** — flags equipment/sensor anomalies and maintenance risk
""")

st.caption(
    "Built for SIH — this is a software prototype using simulated sensor "
    "data, not a connected physical station."
)

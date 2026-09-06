"""PERSON 4 — Optimization Engine page."""

import streamlit as st
from utils.style import apply_style
apply_style()
from ml.optimization.optimization_engine import optimize_dispatch

st.header("⚙️ Energy Optimization Engine")
st.caption(
    "Person 4's module: MILP solver finds the lowest-fuel-cost dispatch "
    "plan (solar + wind + battery + diesel generator)."
)

c1, c2 = st.columns(2)
with c1:
    load_kw = st.slider("Current Load (kW)", 100, 500, 350)
    solar_kw = st.slider("Available Solar (kW)", 0, 300, 100)
with c2:
    wind_kw = st.slider("Available Wind (kW)", 0, 300, 90)
    battery_soc = st.slider("Battery SoC (%)", 20, 100, 65)

if st.button("Run optimization", type="primary"):
    plan = optimize_dispatch(load_kw, solar_kw, wind_kw, battery_soc)
    st.success(f"Solver status: {plan['status']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Solar used", f"{plan['solar_used_kw']} kW")
    m2.metric("Wind used", f"{plan['wind_used_kw']} kW")
    m3.metric("Battery discharge", f"{plan['battery_discharge_kw']} kW")
    m4.metric("Generator output", f"{plan['generator_output_kw']} kW")

    st.info(f"Estimated diesel fuel cost this hour: ₹{plan['estimated_fuel_cost']}")

    fuel_only_cost = load_kw * 0.5
    savings_pct = (
        100 * (1 - plan["estimated_fuel_cost"] / fuel_only_cost)
        if fuel_only_cost
        else 0
    )
    st.metric("Fuel cost saved vs. diesel-only baseline", f"{savings_pct:.0f}%")

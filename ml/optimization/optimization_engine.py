import pulp


def optimize_dispatch(
    load_kw,
    solar_kw,
    wind_kw,
    battery_soc_pct,
    battery_capacity_kwh=500,
    max_battery_rate_kw=100,
    generator_cost_per_kwh=0.5,
    min_soc_pct=20,
):
    """Solves a single-hour dispatch problem and returns the optimal split."""
    prob = pulp.LpProblem("EnergyDispatch", pulp.LpMinimize)

    solar_used = pulp.LpVariable("solar_used", 0, solar_kw)
    wind_used = pulp.LpVariable("wind_used", 0, wind_kw)

    battery_available_kwh = max(
        battery_capacity_kwh * (battery_soc_pct - min_soc_pct) / 100, 0
    )
    battery_discharge = pulp.LpVariable(
        "battery_discharge", 0, min(max_battery_rate_kw, battery_available_kwh)
    )
    generator_output = pulp.LpVariable("generator_output", 0, 1500)

    # Objective: minimize diesel fuel cost (renewables + battery treated as free)
    prob += generator_output * generator_cost_per_kwh

    # Supply must meet demand exactly
    prob += solar_used + wind_used + battery_discharge + generator_output == load_kw

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    return {
        "status": pulp.LpStatus[prob.status],
        "solar_used_kw": round(solar_used.value(), 2),
        "wind_used_kw": round(wind_used.value(), 2),
        "battery_discharge_kw": round(battery_discharge.value(), 2),
        "generator_output_kw": round(generator_output.value(), 2),
        "estimated_fuel_cost": round(
            generator_output.value() * generator_cost_per_kwh, 2
        ),
    }


def optimize_24h_schedule(forecast_df, starting_soc_pct=60):
    """Runs the hourly optimizer across a 24-row forecast dataframe with
    columns: timestamp, load_kw, solar_kw, wind_kw."""
    results = []
    soc = starting_soc_pct
    for _, row in forecast_df.iterrows():
        plan = optimize_dispatch(row["load_kw"], row["solar_kw"], row["wind_kw"], soc)
        soc = max(20, soc - (plan["battery_discharge_kw"] / 500) * 100)
        plan["timestamp"] = row.get("timestamp")
        results.append(plan)
    return results


if __name__ == "__main__":
    print(optimize_dispatch(load_kw=350, solar_kw=120, wind_kw=80, battery_soc_pct=70))

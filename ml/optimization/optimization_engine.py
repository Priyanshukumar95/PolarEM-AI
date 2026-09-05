"""
optimization_engine.py
PERSON 4 — Energy Optimization Engine (MILP via PuLP)

Decides, for a given hour, the lowest-fuel-cost way to meet load using
solar, wind, battery discharge, and the diesel generator as a last resort.

NOTE ON SCOPE: the original brief also called for a Reinforcement Learning
dispatch agent. A genuinely trained, converged RL agent is not realistic to
build AND validate inside a 24-hour hackathon window -- a rushed one would
just be decorative code that doesn't actually learn anything useful. This
MILP solver is the real, working optimizer for your demo. If you want to
gesture at the RL roadmap in your pitch deck, frame it as "future work"
rather than shipping a fake agent.

Run directly:  python ml/optimization/optimization_engine.py
"""

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

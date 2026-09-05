"""
data_generator.py
PERSON 1 — Data Pipeline & Simulation Lead

Generates realistic synthetic sensor data for a polar research station:
load demand, solar generation, wind generation, weather, battery state of
charge and diesel fuel consumption. Also injects labelled anomalies so the
anomaly-detection module has something to learn from.

Run directly:  python simulation/data_generator.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)


def generate_timestamps(start_date="2026-01-01", days=90, freq_hours=1):
    start = pd.to_datetime(start_date)
    periods = int(days * 24 / freq_hours)
    return pd.date_range(start=start, periods=periods, freq=f"{freq_hours}h")


def generate_weather(timestamps):
    """Polar weather: -60C to -20C, seasonal + daily variation."""
    day_of_year = timestamps.dayofyear
    hour = timestamps.hour

    seasonal = -40 + 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    daily = 3 * np.sin(2 * np.pi * hour / 24)
    noise = np.random.normal(0, 2, len(timestamps))
    temperature = np.clip(seasonal + daily + noise, -60, -20)

    wind_speed = np.clip(
        8
        + 5 * np.sin(2 * np.pi * hour / 24 + 1)
        + np.random.normal(0, 3, len(timestamps)),
        0,
        30,
    )
    cloud_cover = np.clip(np.random.beta(2, 2, len(timestamps)) * 100, 0, 100)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "temperature_c": temperature.round(2),
            "wind_speed_ms": wind_speed.round(2),
            "cloud_cover_pct": cloud_cover.round(1),
        }
    )


def generate_solar(weather_df, capacity_kw=300):
    hour = weather_df["timestamp"].dt.hour
    day_of_year = weather_df["timestamp"].dt.dayofyear

    # Polar day/night cycle: usable sun window shrinks for much of the year
    sun_elevation_factor = np.clip(np.sin(2 * np.pi * (day_of_year - 80) / 365), 0, 1)
    hour_factor = np.clip(np.sin(np.pi * (hour - 6) / 12), 0, 1)
    cloud_penalty = 1 - (weather_df["cloud_cover_pct"] / 100) * 0.7

    solar_kw = capacity_kw * sun_elevation_factor * hour_factor * cloud_penalty
    solar_kw += np.random.normal(0, 5, len(weather_df))
    return np.clip(solar_kw, 0, capacity_kw).round(2)


def generate_wind(weather_df, rated_kw=300):
    ws = weather_df["wind_speed_ms"]
    # Simplified turbine power curve: cubic ramp-up, rated plateau, cut-out
    power = np.where(
        ws < 3,
        0,
        np.where(
            ws < 12, rated_kw * ((ws - 3) / 9) ** 3, np.where(ws < 25, rated_kw, 0)
        ),
    )
    power = power + np.random.normal(0, 8, len(weather_df))
    return np.clip(power, 0, rated_kw).round(2)


def generate_load(timestamps, temperature):
    hour = timestamps.hour
    day_of_week = timestamps.dayofweek

    daily_pattern = 250 + 100 * np.sin(2 * np.pi * (hour - 9) / 24)
    weekend_reduction = np.where(day_of_week >= 5, -20, 0)
    heating_load = np.clip(-temperature - 20, 0, None) * 3  # colder -> more heating
    noise = np.random.normal(0, 15, len(timestamps))

    load_kw = daily_pattern + weekend_reduction + heating_load + noise
    return np.clip(load_kw, 100, 500).round(2)


def inject_anomalies(df, n_anomalies=40, seed=42):
    """Randomly injects equipment-failure-like spikes/drops for training a detector."""
    rng = np.random.default_rng(seed)
    df = df.copy()
    df["is_anomaly"] = 0
    idx = rng.choice(df.index, size=n_anomalies, replace=False)
    for i in idx:
        kind = rng.choice(["spike", "drop", "flatline"])
        if kind == "spike":
            df.loc[i, "load_kw"] *= rng.uniform(1.5, 2.2)
        elif kind == "drop":
            df.loc[i, "solar_kw"] = 0
            df.loc[i, "wind_kw"] = 0
        else:
            df.loc[i, "load_kw"] = df["load_kw"].mean()
        df.loc[i, "is_anomaly"] = 1
    return df


def main(days=90, out_dir="data/historical"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    timestamps = generate_timestamps(days=days)
    weather = generate_weather(timestamps)
    weather["solar_kw"] = generate_solar(weather)
    weather["wind_kw"] = generate_wind(weather)
    weather["load_kw"] = generate_load(timestamps, weather["temperature_c"])

    full = inject_anomalies(weather)
    full["battery_soc_pct"] = np.clip(
        50 + (np.cumsum(np.random.normal(0, 1, len(full))) % 40), 10, 100
    ).round(1)
    full["fuel_consumption_l"] = np.clip(
        (full["load_kw"] - full["solar_kw"] - full["wind_kw"]).clip(lower=0) * 0.3
        + np.random.normal(0, 1, len(full)),
        0,
        None,
    ).round(2)

    full.to_csv(out / "full_dataset.csv", index=False)
    weather[["timestamp", "temperature_c", "wind_speed_ms", "cloud_cover_pct"]].to_csv(
        out / "weather.csv", index=False
    )
    full[["timestamp", "load_kw", "is_anomaly"]].to_csv(out / "loads.csv", index=False)
    full[["timestamp", "solar_kw"]].to_csv(out / "solar_generation.csv", index=False)
    full[["timestamp", "wind_kw"]].to_csv(out / "wind_generation.csv", index=False)

    print(
        f"Generated {len(full)} hourly records over {days} days "
        f"-> {out}/full_dataset.csv"
    )
    return full


if __name__ == "__main__":
    main()

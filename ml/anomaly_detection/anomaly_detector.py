"""
anomaly_detector.py
PERSON 4 — Anomaly Detection & Predictive Maintenance

Uses an Isolation Forest to flag hours where sensor readings look abnormal
(equipment faults, sensor glitches). Also includes a simple rolling-average
heuristic that flags a rising fuel-consumption trend as a maintenance risk.

Run directly:  python ml/anomaly_detection/anomaly_detector.py
"""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report

FEATURES = ["load_kw", "solar_kw", "wind_kw", "fuel_consumption_l", "battery_soc_pct"]


def train(
    csv_path="data/historical/full_dataset.csv",
    model_out="ml/models/anomaly_model.pkl",
    contamination=0.02,
):
    df = pd.read_csv(csv_path)
    X = df[FEATURES]

    model = IsolationForest(
        n_estimators=200, contamination=contamination, random_state=42
    )
    model.fit(X)

    preds = model.predict(X)  # -1 = anomaly, 1 = normal
    df["predicted_anomaly"] = (preds == -1).astype(int)

    if "is_anomaly" in df.columns:
        print(classification_report(df["is_anomaly"], df["predicted_anomaly"]))

    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_out)
    return model


def detect(model, readings_df):
    X = readings_df[FEATURES]
    preds = model.predict(X)
    out = readings_df.copy()
    out["is_anomaly"] = (preds == -1).astype(int)
    out["anomaly_score"] = model.decision_function(X)
    return out


def predictive_maintenance_flags(df, fuel_threshold_pct_increase=40):
    """Flags a sustained rise in fuel consumption above the early baseline
    as a generator maintenance risk."""
    df = df.copy()
    df["fuel_rolling_avg"] = df["fuel_consumption_l"].rolling(24, min_periods=1).mean()
    baseline = df["fuel_rolling_avg"].iloc[:24].mean()
    df["maintenance_risk"] = df["fuel_rolling_avg"] > baseline * (
        1 + fuel_threshold_pct_increase / 100
    )
    return df


if __name__ == "__main__":
    train()

"""
renewable_forecast.py
PERSON 3 — Renewable Energy Forecasting (Solar + Wind)

Two lightweight XGBoost regressors: one predicts solar output from time-of-day
+ season + cloud cover, the other predicts wind output from time-of-day +
season + wind speed.

Run directly:  python ml/forecasting/renewable_forecast.py
"""

import pandas as pd
import joblib
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

SOLAR_FEATURES = ["hour", "day_of_year", "cloud_cover_pct"]
WIND_FEATURES = ["hour", "day_of_year", "wind_speed_ms"]


def build_features(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_year"] = df["timestamp"].dt.dayofyear
    return df


def _train_generic(df, features, target, model_out):
    X, y = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = XGBRegressor(
        n_estimators=300, max_depth=5, learning_rate=0.1, random_state=42
    )
    model.fit(X_train, y_train)

    # MAPE is a poor metric here: solar/wind output is legitimately zero for
    # long polar-night / calm-wind stretches, which makes percentage error
    # blow up even when the absolute error is tiny. Report MAE/RMSE instead.
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    print(f"{target} forecast -> MAE: {mae:.2f} kW | RMSE: {rmse:.2f} kW")

    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_out)
    return model


def train_solar(
    csv_path="data/historical/full_dataset.csv", model_out="ml/models/solar_model.pkl"
):
    df = build_features(pd.read_csv(csv_path))
    return _train_generic(df, SOLAR_FEATURES, "solar_kw", model_out)


def train_wind(
    csv_path="data/historical/full_dataset.csv", model_out="ml/models/wind_model.pkl"
):
    df = build_features(pd.read_csv(csv_path))
    return _train_generic(df, WIND_FEATURES, "wind_kw", model_out)


if __name__ == "__main__":
    train_solar()
    train_wind()

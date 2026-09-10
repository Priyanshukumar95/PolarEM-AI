import pandas as pd
import joblib
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from sklearn.model_selection import train_test_split

FEATURES = [
    "hour",
    "day_of_week",
    "day_of_year",
    "temperature_c",
    "load_lag_1",
    "load_lag_24",
    "load_rolling_mean_24",
]


def build_features(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["day_of_year"] = df["timestamp"].dt.dayofyear
    df["load_lag_1"] = df["load_kw"].shift(1)
    df["load_lag_24"] = df["load_kw"].shift(24)
    df["load_rolling_mean_24"] = df["load_kw"].rolling(24).mean()
    return df.dropna().reset_index(drop=True)


def train(
    csv_path="data/historical/full_dataset.csv", model_out="ml/models/xgboost_load.pkl"
):
    df = pd.read_csv(csv_path)
    df = build_features(df)
    X, y = df[FEATURES], df["load_kw"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = XGBRegressor(
        n_estimators=500, max_depth=7, learning_rate=0.1, subsample=0.8, random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mape = mean_absolute_percentage_error(y_test, preds) * 100
    rmse = mean_squared_error(y_test, preds) ** 0.5
    print(f"XGBoost Load Forecast -> MAPE: {mape:.2f}% | RMSE: {rmse:.2f} kW")

    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_out)
    return model, {"mape": mape, "rmse": rmse}


def forecast_next_24h(model, history_df):
    """Iteratively forecasts the next 24 hours, feeding each prediction back
    in as a lag feature for the next step."""
    history = build_features(history_df).copy()
    preds = []
    last_ts = pd.to_datetime(history["timestamp"].iloc[-1])

    for step in range(24):
        ts = last_ts + pd.Timedelta(hours=step + 1)
        row = {
            "hour": ts.hour,
            "day_of_week": ts.dayofweek,
            "day_of_year": ts.dayofyear,
            "temperature_c": history["temperature_c"].iloc[-24:].mean(),
            "load_lag_1": history["load_kw"].iloc[-1],
            "load_lag_24": history["load_kw"].iloc[-24],
            "load_rolling_mean_24": history["load_kw"].iloc[-24:].mean(),
        }
        pred = float(model.predict(pd.DataFrame([row]))[0])
        preds.append({"timestamp": ts, "predicted_load_kw": round(pred, 2)})

        new_row = row.copy()
        new_row["timestamp"] = ts
        new_row["load_kw"] = pred
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    return pd.DataFrame(preds)


if __name__ == "__main__":
    train()

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from tensorflow.keras import layers


def make_sequences(values, window=24):
    X, y = [], []
    for i in range(len(values) - window):
        X.append(values[i : i + window])
        y.append(values[i + window])
    return np.array(X), np.array(y)


def train(
    csv_path="data/historical/full_dataset.csv",
    model_out="ml/models/lstm_load.h5",
    scaler_out="ml/models/lstm_scaler.pkl",
    window=24,
    epochs=10,
):
    df = pd.read_csv(csv_path)
    values = df["load_kw"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = make_sequences(scaled, window)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    split = int(len(X) * 0.8)
    X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]

    model = keras.Sequential(
        [
            layers.LSTM(32, input_shape=(window, 1)),
            layers.Dense(16, activation="relu"),
            layers.Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse")
    model.fit(
        X_train,
        y_train,
        epochs=epochs,
        batch_size=32,
        validation_data=(X_test, y_test),
        verbose=1,
    )

    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    model.save(model_out)
    joblib.dump(scaler, scaler_out)
    return model, scaler


if __name__ == "__main__":
    train()

# AI-Driven Smart Energy Management System — Polar Research Stations

SIH prototype: a Streamlit dashboard that simulates a polar research
station's power system and demonstrates AI-driven load forecasting,
renewable generation forecasting, optimal energy dispatch, and anomaly
detection.

## Modules

| Module | File(s) | Owner |
|---|---|---|
| Data simulation | `data_generator.py` | Person 1 |
| Load forecasting (XGBoost, primary) | `load_forecast_xgboost.py` | Person 2 |
| Load forecasting (Prophet, cross-check) | `load_forecast_prophet.py` | Person 2 |
| Load forecasting (LSTM, optional) | `load_forecast_lstm.py` | Person 2 |
| Renewable forecasting (solar+wind) | `renewable_forecast.py` | Person 3 |
| Optimization engine (MILP) | `optimization_engine.py` | Person 4 |
| Anomaly detection | `anomaly_detector.py` | Person 4 |
| Dashboard (all pages) | `app.py`, `pages/*.py` | Person 5 |

(Full paths for every file are under `ml/forecasting/`, `ml/optimization/`,
and `ml/anomaly_detection/` — see the project tree in `DEPLOYMENT_GUIDE.pdf`.)

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Generate data and train all models (do this once before your demo)

```bash
python simulation/data_generator.py
python ml/forecasting/load_forecast_xgboost.py
python ml/forecasting/renewable_forecast.py
python ml/optimization/optimization_engine.py
python ml/anomaly_detection/anomaly_detector.py
```

This creates `data/historical/full_dataset.csv` and the trained model files
in `ml/models/`. Commit these to the repo — see the deployment guide for why.

## Run the dashboard

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501).

## Deployment

Deployed on Streamlit Community Cloud — see `DEPLOYMENT_GUIDE.pdf` for the
full step-by-step (GitHub push + Streamlit Cloud setup + troubleshooting).

## Scope notes

This is a software prototype built around simulated sensor data, not a
system connected to physical station hardware. The optimization engine is a
real, working Mixed-Integer Linear Program (MILP) solved with PuLP/CBC. A
trained Reinforcement Learning dispatch agent was scoped out as unrealistic
to build and validate within a 24-hour build window — it's called out as
future work rather than shipped as decorative, unvalidated code.

from fastapi import FastAPI
from ingest import fetch_prices, fetch_wind
from features import build_features
import mlflow



app = FastAPI()

# runs once when server starts
runs = mlflow.search_runs(search_all_experiments=True)
best_run = runs.sort_values("metrics.mae").iloc[0]
run_id = best_run["run_id"]
model = mlflow.lightgbm.load_model(f"runs:/{run_id}/model")

@app.get("/forecast")
def forecast():
    df_price = fetch_prices()
    df_wind = fetch_wind()
    features = build_features(df_price, df_wind)

    timestamps = features.iloc[-24:]["time"]
    features = features.drop(["time", "price"], axis=1)
    next_24 = features.iloc[-24:]
    predictions = model.predict(next_24)

    results = [
    {"timestamp": str(ts), "forecast_dkk_mwh": round(pred, 2)}
    for ts, pred in zip(timestamps, predictions)
    ]

    return results

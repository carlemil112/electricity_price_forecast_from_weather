from fastapi import FastAPI
from ingest import fetch_prices, fetch_wind
from features import build_features
import glob
import os
from skops.io import load as skops_load


app = FastAPI()

# Find and load the most recent model
model_files = glob.glob("mlruns/**/model.skops", recursive=True)
latest_model = max(model_files, key=os.path.getmtime)
model = skops_load(latest_model, trusted=[
    "lightgbm.sklearn.LGBMRegressor",
    "lightgbm.basic.Booster",
    "collections.OrderedDict"
])

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
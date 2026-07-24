import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prefect import flow, task
from ingest import fetch_prices, fetch_wind
from features import build_features, split_features
from train import train_model, evaluate_model


@task
def fetch_data():
    df_prices = fetch_prices()
    df_wind = fetch_wind()
    df_prices.to_parquet("data/prices.parquet")
    df_wind.to_parquet("data/wind.parquet")
    

@task
def assemble_features():
    df_prices = pd.read_parquet("data/prices.parquet")
    df_wind = pd.read_parquet("data/wind.parquet")

    df_features = build_features(df_prices, df_wind)
    df_train, df_test = split_features(df_features)
    return df_train, df_test


@task
def train_test(df_train, df_test):
    model = train_model(df_train)
    mae, rmse = evaluate_model(model, df_test)



@flow
def daily_pipeline():
    fetch_data()
    df_train, df_test = assemble_features()
    train_test(df_train, df_test)



if __name__ == "__main__":
    daily_pipeline.serve(
        name="daily-forecast",
        cron="0 6 * * *" #every day at 06:00
    )
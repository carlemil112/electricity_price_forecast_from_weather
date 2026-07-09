import os
import datetime as dt
import requests
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path



def fetch_prices(days=90):
    """Fetch day-ahead prices from Energi Data Service. Returns hourly dataframe with columns [time, price]."""
    # Set time range
    end_time = dt.datetime.now(dt.timezone.utc)
    start_time = end_time - dt.timedelta(days=days)


    # Build request
    url = "https://api.energidataservice.dk/dataset/DayAheadPrices"
    params = {
        "start": start_time.strftime("%Y-%m-%dT%H:%M"),
        "end":   end_time.strftime("%Y-%m-%dT%H:%M"),
        "filter": '{"PriceArea":["DK1"]}',
        "limit": 10000,
    }

    # call API
    response = requests.get(url, params=params, timeout=60)

    # Parse
    records = response.json()["records"]

    # Build dataframe
    df_prices = pd.DataFrame(records)

    df_prices["time"] = pd.to_datetime(df_prices["TimeUTC"], utc=True)
    df_prices = df_prices[["time", "DayAheadPriceDKK"]]
    df_prices = df_prices.rename(columns={"DayAheadPriceDKK": "price"})
    df_prices = df_prices.sort_values("time").reset_index(drop=True)

    df_prices = df_prices.set_index("time").resample("1h").mean().reset_index()

    return df_prices


def fetch_wind(days=90):
    """Fetch wind speed observations from DMI. Returns hourly dataframe with columns [time, wind_ms]."""
    # Set time range
    end_time = dt.datetime.now(dt.timezone.utc)
    start_time = end_time - dt.timedelta(days=days)    


    #Build request
    url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"
    params = {
        "parameterId": "wind_speed",
        "stationId": "06073",
        "datetime": f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "limit": 10000,
    }

    # Call API
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    features = response.json()["features"]

    # Parse into dataframe
    rows = [
        {
            "time": f["properties"]["observed"],
            "wind_ms": f["properties"]["value"]
        }
        for f in features
    ]

    df_wind = pd.DataFrame(rows)
    df_wind["time"] = pd.to_datetime(df_wind["time"], utc=True)

    # Resample to hourly (observations are every 10 minutes)
    df_wind = df_wind.set_index("time").resample("1h").mean().reset_index()

    return df_wind
    

if __name__ == "__main__":
    df_prices = fetch_prices()
    df_wind = fetch_wind()  

    print(df_prices.shape)
    print(df_wind.shape)

    Path("data").mkdir(exist_ok=True)

    df_prices.to_parquet("data/df_prices.parquet")
    df_wind.to_parquet("data/df_wind.parquet")
import os
import datetime as dt

import requests
import pandas as pd
import matplotlib.pyplot as plt

"""
Step 1: Fetch electricity prices
"""

# Set time range
end_time = dt.datetime.now(dt.timezone.utc)
start_time = end_time - dt.timedelta(days=30)


# Build request
url = "https://api.energidataservice.dk/dataset/DayAheadPrices"
params = {
    "start": start_time.strftime("%Y-%m-%dT%H:%M"),
    "end":   end_time.strftime("%Y-%m-%dT%H:%M"),
    "filter": '{"PriceArea":["DK1"]}',
    "limit": 10000,
}

# call API
response = requests.get(url, params=params, timeout=30)

# Parse
records = response.json()["records"]
print(records[0])

# Build dataframe
df_prices = pd.DataFrame(records)

df_prices["time"] = pd.to_datetime(df_prices["TimeUTC"], utc=True)
df_prices = df_prices[["time", "DayAheadPriceDKK"]]
df_prices = df_prices.rename(columns={"DayAheadPriceDKK": "price"})
df_prices = df_prices.sort_values("time").reset_index(drop=True)

df_prices = df_prices.set_index("time").resample("1h").mean().reset_index()


"""
Step 2 - Fetch wind speed from DMO
"""
# Build request
url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"
params = {
    "parameterId": "wind_speed",
    "stationId": "06073", # Århus!
    "datetime": f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
    "limit": 10000,
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

features = response.json()["features"]
#print(features[0]) 


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



"""
Step 3: Align and correlate
"""

#Sort both before merging
df_prices = df_prices.sort_values("time")
df_wind = df_wind.sort_values("time")

# merge on nearest timestamp within 1 hour tolerance
merged = pd.merge_asof(
    df_prices,
    df_wind,
    on="time",
    direction="nearest",
    tolerance=pd.Timedelta("1h")
)

# Drop rows where either value is missing
merged = merged.dropna()

# Correlation
corr = merged["price"].corr(merged["wind_ms"])
print(f"Rows: {len(merged)}")
print(f"Correlation: {corr:.3f}")  # expect negativ

print(f"Price rows: {len(df_prices)}")
print(f"Wind rows: {len(df_wind)}")
print(df_wind.head())
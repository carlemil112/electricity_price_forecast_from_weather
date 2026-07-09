import pandas as pd
import datetime as dt



def build_features(df_prices, df_wind) -> pd.DataFrame:
    """Merge price and wind data, add lag features, rolling averages and calendar features. Returns model-ready dataframe."""
    merged = pd.merge_asof(
    df_prices,
    df_wind,
    on="time",
    direction="nearest",
    tolerance=pd.Timedelta("1h")
    )
    #Calendar features 
    merged["hour"]       = merged["time"].dt.hour
    merged["day_of_week"] = merged["time"].dt.dayofweek
    merged["month"]      = merged["time"].dt.month
    merged["is_weekend"] = merged["time"].dt.dayofweek >= 5

    # lag features on price column
    merged["price_lag_24"] = merged["price"].shift(24)
    merged["price_lag_48"] = merged["price"].shift(48)
    merged["price_lag_168"] = merged["price"].shift(168)

    # rolling averages on price column
    merged["price_rolling_24"] = merged["price"].rolling(24).mean()
    merged["price_rolling_168"] = merged["price"].rolling(168).mean()

    merged = merged.dropna()
    return merged


def split_features(df, test_days=7):
    """Split dataframe into train and test sets by time. No random shuffling."""
    cutoff = df["time"].max() - pd.Timedelta(days=test_days)
    
    df_train = df[df["time"] <= cutoff]
    df_test = df[df["time"] > cutoff]

    return df_train, df_test




if __name__ == "__main__":
    df_prices = pd.read_parquet("data/df_prices.parquet")
    df_wind = pd.read_parquet("data/df_wind.parquet")
    df_features = build_features(df_prices, df_wind)
    print(df_features.shape)
    print(df_features.head())
    
    df_train, df_test = split_features(df_features)

    print(df_train, df_test)
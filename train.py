import lightgbm as lgb
from features import build_features, split_features
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import pandas as pd
import mlflow
import os
os.environ["LIGHTGBM_VERBOSITY"] = "-1"
import warnings
warnings.filterwarnings("ignore")

def train_model(df_train):
    """Train a LightGBM model on the training set. Returns trained model."""
    X = df_train.drop(["time", "price"], axis=1)
    y = df_train["price"]

    model = lgb.LGBMRegressor(
        n_estimators=100,
        max_depth=4,
        min_child_samples=10
    )

    model.fit(X, y, callbacks=[lgb.log_evaluation(period=-1)])

    return model


def evaluate_model(model, df_test):
    """Evaluate model on test set. Prints MAE and RMSE."""
    X = df_test.drop(["time", "price"], axis=1)
    y = df_test["price"]

    y_pred = model.predict(X)

    mae = mean_absolute_error(y, y_pred)
    rmse = root_mean_squared_error(y, y_pred)

    # Baseline based on average price every time vs model
    baseline = y.mean()
    baseline_mae = mean_absolute_error(y, [baseline] * len(y))

    return mae, rmse



if __name__ == "__main__":
    df_prices = pd.read_parquet("data/df_prices.parquet")
    df_wind = pd.read_parquet("data/df_wind.parquet")

    df_features = build_features(df_prices, df_wind)
    df_train, df_test = split_features(df_features)


    with mlflow.start_run():
        #logging of parameters:
        mlflow.log_param("max_depth", 4)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("min_child_samples", 10)

        model = train_model(df_train)
        mlflow.lightgbm.log_model(model, "model")

        mae, rmse = evaluate_model(model, df_test)

        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)


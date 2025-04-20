"""Processors for the model training step of the worklow."""
import logging
import os.path as op
import pandas as pd
import numpy as np
import gc
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error#,mean_absolute_percentage_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error
from sklearn.preprocessing import StandardScaler

from sklearn.pipeline import Pipeline

from ta_lib.core.api import (
    get_dataframe,
    get_feature_names_from_column_transformer,
    get_package_path,
    load_dataset,
    load_pipeline,
    register_processor,
    save_pipeline,
    save_dataset,
    DEFAULT_ARTIFACTS_PATH
)
from ta_lib.regression.api import SKLStatsmodelOLS
from feature_engineering import transform_features
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

logger = logging.getLogger(__name__)

@register_processor("model-gen", "train-test")
def create_training_datasets(context, params):
    """
    Prepares training and test datasets for time series modeling using lag features.

    This processor:
    - Filters the dataset for a specific `claim_id` (default: 8).
    - Generates lag features for `search_volume` and `sales_dollars_value`.
    - Splits the data using a time series-aware split.
    - Tunes the number of lags based on Mean Absolute Percentage Error (MAPE).
    - Scales features using StandardScaler.
    - Saves the best train-test split based on minimum MAPE.

    Parameters
    ----------
    context : object
        A custom context object used to load and save datasets.
    params : dict
        Configuration dictionary. Optional keys:
            - 'claim_id': int, claim identifier to filter the data.
            - 'target_column': str, target column to predict (default: "sales_dollars_value").
            - 'test_size': float, ratio of data to reserve for testing (default: 0.3).

    Returns
    -------
    None
        Saves the training and test features/targets in:
        - train/FnB/features
        - test/FnB/features
        - train/FnB/target
        - test/FnB/target
    """

    logger.info("Loading data from processes directory")

    client_data = load_dataset(context, "processed/FnB/client_data")
    claim_id = params.get("claim_id", 8)

    exp = client_data[client_data['claim_id'] == claim_id]
    exp.fillna(0, inplace=True)
    exp.sort_values(by='date', inplace=True)
    exp.set_index('date', inplace=True)

    def create_lagged_features(data, max_lag):
        df = data.copy()
        for i in range(1, max_lag + 1):
            df[f"search_lag_{i}"] = df["search_volume"].shift(i)
            df[f"sales_lag_{i}"] = df["sales_dollars_value"].shift(i)
        return df.dropna()

    def timeseries_train_test_split(X, y, test_size=0.3):
        test_index = int(len(X) * (1 - test_size))
        return X.iloc[:test_index], X.iloc[test_index:], y.iloc[:test_index], y.iloc[test_index:]

    def mean_absolute_percentage_error(y_true, y_pred): 
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    logger.info("Performing Hyper Parameter Tuning")
    min_mape = float("inf")
    best_lag = 0
    best_split = None
    scaler = StandardScaler()
    target = params.get("target_column", "sales_dollars_value")
    test_size = params.get("test_size", 0.3)
    for lag in range(1, 19):
        lagged_data = create_lagged_features(exp, lag)
        y = lagged_data[target]
        X = lagged_data.drop(['sales_dollars_value', 'sales_units_value', 'sales_lbs_value', 'vendor', 'claim_id'], axis=1, errors='ignore')

        X_train, X_test, y_train, y_test = timeseries_train_test_split(X, y, test_size)

        X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
        X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns, index=X_test.index)


        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        mape = mean_absolute_percentage_error(y_test, y_pred)

        if mape < min_mape:
            min_mape = mape
            best_lag = lag
            best_split = (X_train_scaled, X_test_scaled, y_train, y_test)

        # logger.info(f"Lag {lag}: MAPE = {mape:.4f}")

    # Save the best result
    X_train_scaled, X_test_scaled, y_train, y_test = best_split

    save_dataset(context, X_train_scaled, "train/FnB/features")
    save_dataset(context, X_test_scaled, "test/FnB/features")
    save_dataset(context, y_train, "train/FnB/target")
    save_dataset(context, y_test, "test/FnB/target")

    logger.info(f"Best lag: {best_lag} with MAPE = {min_mape:.4f}")

    logger.info("Saved the train and test data to respective directories")

    del client_data, exp, best_split, X_train_scaled, X_test_scaled, y_train, y_test, scaler
    gc.collect()

@register_processor("model-gen", "train-model")
def train_model(context, params):
    """
    Trains a Linear Regression model on the training dataset.

    This processor:
    - Loads the training features and target.
    - Trains a Linear Regression model.
    - Saves the trained model to the artifacts directory.

    Parameters
    ----------
    context : object
        A custom context object used to access and manage datasets and pipelines.
    params : dict
        Parameters for future extensibility (currently unused).

    Returns
    -------
    None
        The trained model is saved as 'linear_model.pkl' in the artifacts directory.
    """

    artifacts_folder = DEFAULT_ARTIFACTS_PATH

    X_train = load_dataset(context, "train/FnB/features")
    y_train = load_dataset(context, "train/FnB/target")

    model = LinearRegression()
    model.fit(X_train, y_train)

    joblib.dump(model, op.abspath(op.join(artifacts_folder, "linear_model.pkl")))

    logger.info("Trained and saved the model to artifacts directory")
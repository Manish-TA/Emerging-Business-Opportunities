"""Processors for the model training step of the worklow."""
import logging
import os.path as op

from sklearn.pipeline import Pipeline

from ta_lib.core.api import (
    get_dataframe,
    get_feature_names_from_column_transformer,
    get_package_path,
    load_dataset,
    load_pipeline,
    register_processor,
    save_pipeline,
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


@register_processor("model-gen", "train-model")
def train_model(context, params):
    """
    Trains a Random Forest model with hyperparameter tuning on the training dataset.

    Parameters
    ----------
    test_size: the split ratio
    target_column : str, optional
        The target column to predict (default: "median_house_value").
    context : The context object
    params : parameters, if any for the function to run

    Returns
    -------
    RandomForestRegressor
        The best Random Forest model from hyperparameter tuning.
    """
    artifacts_folder = DEFAULT_ARTIFACTS_PATH

    input_features_ds = "processed/housing/features"
    input_target_ds = "processed/housing/target"
    
    # load training datasets
    X_train = load_dataset(context, input_features_ds)
    y_train = load_dataset(context, input_target_ds)

    logging.info("Defining hyperparameter search space...")
    param_distributions = {
        "n_estimators": randint(50, 200),
        "max_features": randint(2, 8),
        "max_depth": randint(10, 50),
    }

    model = RandomForestRegressor(random_state=42)
    random_search = RandomizedSearchCV(
        model,
        param_distributions=param_distributions,
        n_iter=20,
        scoring="neg_mean_squared_error",
        cv=5,
        random_state=42,
        n_jobs=-1,
    )
    y_train = y_train.values.ravel()
    logging.info("Starting hyperparameter tuning...")
    random_search.fit(X_train, y_train)
    best_model = random_search.best_estimator_
    logging.info(f"Best model parameters: {random_search.best_params_}")
    joblib.dump(best_model, op.abspath(op.join(artifacts_folder, "random_forest_model.pkl")))
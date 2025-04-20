"""Processors for the model scoring/evaluation step of the worklow."""
import os.path as op

from ta_lib.core.api import (get_dataframe,
                             get_feature_names_from_column_transformer,
                             get_package_path, hash_object, load_dataset,
                             load_pipeline, register_processor, save_dataset, DEFAULT_ARTIFACTS_PATH)
import joblib
import mlflow
import numpy as np
import pandas as pd
import logging
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

logger = logging.getLogger(__name__)

@register_processor("model-eval", "score-model")
def score_model(context, params):
    """
    Scores a trained regression model using test data and logs evaluation metrics.

    This processor:
    - Loads the test feature set and target variable from the data store.
    - Loads the trained model pipeline from the artifacts directory.
    - Generates predictions using the test set.
    - Calculates the Mean Absolute Percentage Error (MAPE).
    - Logs the MAPE value for evaluation.
    - Saves the prediction results to the score directory.

    Parameters
    ----------
    context : object
        A custom context object used to load and save datasets and pipelines.
    params : dict
        Optional parameters for extension. Currently unused.

    Returns
    -------
    None
        The function saves the predictions to "score/FnB/output" and logs MAPE.
    """
    output_ds = "score/FnB/output"

    X_test = load_dataset(context, "test/FnB/features")
    y_test = load_dataset(context, "test/FnB/target")
    
    artifacts_folder = DEFAULT_ARTIFACTS_PATH

    model_pipeline = load_pipeline(op.join(artifacts_folder, "linear_model.pkl"))
    predictions = model_pipeline.predict(X_test)
    mape = mean_absolute_percentage_error(y_test, predictions) * 100
    print(f"MAPE: {mape:.4f}%")
    logger.info(f"MAPE: {mape:.4f}%")
    predictions = pd.DataFrame(predictions)
    save_dataset(context, predictions, output_ds)
    logger.info("Saved the test predictions to test directory")

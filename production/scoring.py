"""Processors for the model scoring/evaluation step of the worklow."""
import os.path as op

from ta_lib.core.api import (get_dataframe,
                             get_feature_names_from_column_transformer,
                             get_package_path, hash_object, load_dataset,
                             load_pipeline, register_processor, save_dataset, DEFAULT_ARTIFACTS_PATH)
from scripts import CombinedAttributesAdder
import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error

@register_processor("model-eval", "score-model")
def score_model(context, params):   
    """
    Loads a trained model and evaluates it on a dataset.

    Parameters
    ----------
    context : The context object
    params : parameters, if any for the function to run

    Returns
    -------
    float
        Root Mean Squared Error (RMSE) on the dataset.
    """
    input_features_ds = "test/housing/features"
    input_target_ds = "test/housing/target"
    output_ds = "score/housing/output"
    
    artifacts_folder = DEFAULT_ARTIFACTS_PATH

    # load test datasets
    test_X = load_dataset(context, input_features_ds)
    test_y = load_dataset(context, input_target_ds)

    # load the feature pipeline and training pipelines
    features_transformer = load_pipeline(op.join(artifacts_folder, "preprocessor.pkl"))
    model_pipeline = load_pipeline(op.join(artifacts_folder, "random_forest_model.pkl"))

    # transform the test dataset
    test_X = features_transformer.transform(test_X)

    # make a prediction
    predictions = model_pipeline.predict(test_X)
    rmse = np.sqrt(mean_squared_error(test_y, predictions))
    print(rmse)
    # store the predictions for any further processing.
    predictions = pd.DataFrame(predictions)
    save_dataset(context, predictions, output_ds)

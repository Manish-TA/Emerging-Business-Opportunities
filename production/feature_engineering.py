"""Processors for the feature engineering step of the worklow.

The step loads cleaned training data, processes the data for outliers,
missing values and any other cleaning steps based on business rules/intuition.

The trained pipeline and any artifacts are then saved to be used in
training/scoring pipelines.
"""
import logging
import os.path as op
import os
import joblib
import pandas as pd

from category_encoders import TargetEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from scripts import CombinedAttributesAdder
from sklearn.preprocessing import OneHotEncoder

from ta_lib.core.api import (
    get_dataframe,
    get_feature_names_from_column_transformer,
    get_package_path,
    load_dataset,
    register_processor,
    save_pipeline,
    save_dataset,
    DEFAULT_ARTIFACTS_PATH
)

from ta_lib.data_processing.api import Outlier

logger = logging.getLogger(__name__)


@register_processor("feat-engg", "transform-features")
def transform_features(context, params):
    """
    Preprocesses data: adds derived features,
    encodes categorical variables, and imputes missing values.

    Parameters
    ----------
    context : The context object
    params : parameters, if any for the function to run

    Returns
    -------
    np.ndarray, pd.Series
        Preprocessed feature matrix and target values.
    """
    input_features_ds = "train/housing/features"
    input_target_ds = "train/housing/target"

    artifacts_folder = DEFAULT_ARTIFACTS_PATH

    # load datasets
    X = load_dataset(context, input_features_ds)
    y = load_dataset(context, input_target_ds)

    categorical_columns = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_columns = X.select_dtypes(include=["number"]).columns.tolist()

    numeric_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("attribs_adder", CombinedAttributesAdder()),
        ]
    )

    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("num", numeric_transformer, numerical_columns),
            ("cat", categorical_transformer, categorical_columns),
        ]
    )

    X_preprocessed = preprocessor.fit_transform(X)
    X_preprocessed = pd.DataFrame(X_preprocessed)
    joblib.dump(preprocessor, op.abspath(op.join(artifacts_folder, "preprocessor.pkl")))
    save_dataset(context, X_preprocessed, "processed/housing/features")
    save_dataset(context, y, "processed/housing/target")
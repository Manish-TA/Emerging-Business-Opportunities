"""Processors for the data cleaning step of the worklow.

The processors in this step, apply the various cleaning steps identified
during EDA to create the training datasets.
"""
import numpy as np
import os
import tarfile
import urllib
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

from ta_lib.core.api import (
    custom_train_test_split,
    load_dataset,
    register_processor,
    save_dataset,
    string_cleaning
)


@register_processor("data-cleaning", "fetch-data")
def fetch_housing_data(context, params):
    """
    Downloads and extracts the housing data from the specified URL.

    Parameters
    ----------
    housing_url : str
        URL of the housing data tar file.
    housing_path : str
        Directory where the raw housing data will be saved and extracted.

    Raises
    ------
    Exception
        If there is an error during downloading or extraction.
    """
    housing_url = params["housing_url"]
    housing_path = params["housing_path"]
    os.makedirs(housing_path, exist_ok=True)
    tgz_path = os.path.join(housing_path, "housing.tgz")
    urllib.request.urlretrieve(housing_url, tgz_path)
    with tarfile.open(tgz_path) as housing_tgz:
        housing_tgz.extractall(path=housing_path)



@register_processor("data-cleaning", "housing")
def clean_table(context, params):
    """
    Clean the data in housing table
    """

    input_dataset = "raw/housing"
    output_dataset = "cleaned/housing"

    # load dataset
    product_df = load_dataset(context, input_dataset)

    product_df_clean = (
        product_df
    )
    # save the dataset
    save_dataset(context, product_df_clean, output_dataset)

@register_processor("data-cleaning", "train-test")
def create_training_datasets(context, params):
    """
    Splits the housing dataset into training and validation sets using
    StratifiedShuffleSplit to ensure similar income category distributions.

    Parameters
    ----------
    housing_path : str
        Path to the directory containing the raw housing data file (CSV).
    output_dir : str
        Directory where the processed training and validation data will be saved.

    Raises
    ------
    FileNotFoundError
        If the input dataset file is not found.
    """
    input_dataset = "cleaned/housing"
    output_train_features = "train/housing/features"
    output_train_target = "train/housing/target"
    output_test_features = "test/housing/features"
    output_test_target = "test/housing/target"
    
    # load dataset
    data = load_dataset(context, input_dataset)

    data["income_cat"] = pd.cut(
        data["median_income"],
        bins=[0.0, 1.5, 3.0, 4.5, 6.0, np.inf],
        labels=[1, 2, 3, 4, 5],
    )

    strat_split = StratifiedShuffleSplit(n_splits=1, test_size=params["test_size"], random_state=42)
    for train_index, val_index in strat_split.split(data, data["income_cat"]):
        train_set = data.loc[train_index].drop("income_cat", axis=1)
        val_set = data.loc[val_index].drop("income_cat", axis=1)


    # split train dataset into features and target
    target_col = params["target"]
    train_X, train_y = (
        train_set
        # split the dataset to train and test
        .get_features_targets(target_column_names=target_col)
    )

    # save the train dataset
    save_dataset(context, train_X, output_train_features)
    save_dataset(context, train_y, output_train_target)

    # split test dataset into features and target
    test_X, test_y = (
        val_set
        # split the dataset to train and test
        .get_features_targets(target_column_names=target_col)
    )

    # save the datasets
    save_dataset(context, test_X, output_test_features)
    save_dataset(context, test_y, output_test_target)

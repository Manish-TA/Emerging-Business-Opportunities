"""Processors for the data cleaning step of the worklow.

The processors in this step, apply the various cleaning steps identified
during EDA to create the training datasets.
"""
import numpy as np
import os
import tarfile
import urllib
import gc
import logging
import pandas as pd
from datetime import timedelta
from sklearn.model_selection import StratifiedShuffleSplit

from ta_lib.core.api import (
    custom_train_test_split,
    load_dataset,
    register_processor,
    save_dataset,
    string_cleaning
)

logger = logging.getLogger(__name__)

@register_processor("data-cleaning", "clean-fnb")
def fetch_clean_fnb_data(context, params):
    """
    Cleans raw F&B datasets and saves cleaned versions to the cleaned directory.

    This function loads multiple raw datasets (sales, social media, Google search, 
    theme-product relationships, etc.), applies cleaning steps such as renaming, 
    formatting dates, removing duplicates, handling missing values, and standardizing 
    column names. The cleaned datasets are saved for use in later steps like 
    feature engineering and modeling.

    Parameters
    ----------
    context : object
        A custom context object used to load and save datasets.
    params : dict
        Optional parameters for future extension. Currently unused.

    Returns
    -------
    None
        The cleaned datasets are saved to the 'cleaned/FnB/' directory using the 
        context's save_dataset method.
    """
    logger.info("Loading datasets......")

    sales_data = load_dataset(context, "raw/FnB/sales_data")
    social_media_data = load_dataset(context, "raw/FnB/social_media_data")
    google_search_data = load_dataset(context, "raw/FnB/google_search_data")
    Theme_product_list = load_dataset(context, "raw/FnB/theme_product_list")
    Theme_list = load_dataset(context, "raw/FnB/theme_list")
    product_manufacturer_list = load_dataset(context, "raw/FnB/product_manufacturer_list")
    
    logger.info("Loaded datasets from raw directory")

    sales_data_clean = (
        sales_data
        .copy()
        .change_type(['sales_dollars_value'], np.int64)
        .to_datetime('system_calendar_key_N', format='%Y%m%d')
        .rename_columns({'system_calendar_key_N': 'date'})
        .clean_names(case_type='snake')
    )

    social_media_data_clean = (
        social_media_data
        .copy()
        .replace({'': np.NaN})
        .dropna(axis = 0)
        .change_type(['Theme Id'], np.int64)
        .to_datetime('published_date')
        .rename_columns({'Theme Id': 'claim_id' ,'published_date' : 'date' } )                                                                                                                               
        .clean_names(case_type='snake')
        .drop_duplicates()
    )

    theme_product_list_clean= (
        Theme_product_list
        .copy()                                                                                                                               
        .clean_names(case_type='snake')
    )

    product_manufacturer_list_clean = (
        product_manufacturer_list
        .copy()
        .drop(['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6'], axis=1)                                                                                                               
        .clean_names(case_type='snake')
    )

    theme_list_clean = (
        Theme_list
        .copy()
        .passthrough()    
        .replace({'': np.NaN})
        .clean_names(case_type='snake')
    )

    google_search_data_clean = (
        google_search_data
        .copy()
        .replace({'': np.NaN})
        .to_datetime('date', format='%d-%m-%Y')
        .sort_values(by=['searchVolume'],ascending=False)
        .rename_columns({'year_new' : 'year'})
        .drop_duplicates(subset = ['date' , 'Claim_ID' , 'platform'],keep = 'first').reset_index(drop = True)
        .clean_names(case_type='snake')    
    )

    logger.info("All datasets are cleaned and stored in cleaned directory")

    save_dataset(context, sales_data_clean, "cleaned/FnB/sales_data")
    save_dataset(context, social_media_data_clean, "cleaned/FnB/social_media_data")
    save_dataset(context, google_search_data_clean, "cleaned/FnB/google_search_data")
    save_dataset(context, theme_product_list_clean, "cleaned/FnB/theme_product_list")
    save_dataset(context, theme_list_clean, "cleaned/FnB/theme_list")
    save_dataset(context, product_manufacturer_list_clean, "cleaned/FnB/product_manufacturer_list")

    del (
        sales_data, social_media_data, google_search_data, Theme_product_list, 
        Theme_list, product_manufacturer_list, 
        sales_data_clean, social_media_data_clean, google_search_data_clean, 
        theme_product_list_clean, theme_list_clean, product_manufacturer_list_clean
    )
    gc.collect()
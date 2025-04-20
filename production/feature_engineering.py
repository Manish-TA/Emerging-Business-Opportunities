"""Processors for the feature engineering step of the worklow.

The step loads cleaned training data, processes the data for outliers,
missing values and any other cleaning steps based on business rules/intuition.

The trained pipeline and any artifacts are then saved to be used in
training/scoring pipelines.
"""
import logging
import os.path as op
import os
import gc
import numpy as np
import joblib
from datetime import timedelta
import pandas as pd

from category_encoders import TargetEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
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
    Performs feature engineering on cleaned F&B datasets and saves the processed dataset.

    This function:
    - Loads cleaned sales, social media, Google search, and metadata tables.
    - Creates time-based features such as month and ISO week number.
    - Aggregates data weekly per claim and product.
    - Merges datasets to create a unified, enriched dataset.
    - Computes derived metrics like per unit value, per lbs value, etc.
    - Filters for a specific vendor (e.g., vendor 'A') to isolate client-specific data.
    - Saves the final feature-engineered DataFrame to the processed directory.

    Parameters
    ----------
    context : object
        A custom context object used to load and save datasets.
    params : dict
        Optional parameters for flexibility or future extensions. Currently unused.

    Returns
    -------
    None
        The resulting processed dataset is saved to "processed/FnB/client_data".
    """

    logger.info("Loading data from cleaned directory to merge the datasets")

    google_search_data_clean = load_dataset(context, "cleaned/FnB/google_search_data")
    sales_data_clean = load_dataset(context, "cleaned/FnB/sales_data")
    social_media_data_clean = load_dataset(context, "cleaned/FnB/social_media_data")
    theme_product_list_clean = load_dataset(context, "cleaned/FnB/theme_product_list")
    theme_list_clean = load_dataset(context, "cleaned/FnB/theme_list")
    product_manufacturer_list_clean = load_dataset(context, "cleaned/FnB/product_manufacturer_list")
    google_search_data_clean["date"]= pd.to_datetime(google_search_data_clean["date"])
    google_search_data_clean['month'] = google_search_data_clean['date'].dt.month
    google_search_data_clean['month_name'] = google_search_data_clean['date'].dt.month_name().str[0:3]
    google_search_data_clean['week_number']=pd.Series(google_search_data_clean['date']+timedelta(1)).dt.isocalendar().week

    social_media_data_clean['date'] = pd.to_datetime(social_media_data_clean['date'])
    social_media_data_clean['year'] = social_media_data_clean['date'].dt.year
    social_media_data_clean['month'] = social_media_data_clean['date'].dt.month
    social_media_data_clean['month_name'] = social_media_data_clean['date'].dt.month_name().str[0:3]
    social_media_data_clean['week_number']=pd.Series(social_media_data_clean['date']+timedelta(1)).dt.isocalendar().week

    sales_data_clean['date'] = pd.to_datetime(sales_data_clean['date'])
    sales_data_clean['year'] = sales_data_clean['date'].dt.year
    sales_data_clean['week_number'] = sales_data_clean['date'].dt.isocalendar().week
    sales_data_clean['month'] = sales_data_clean['date'].dt.month
    sales_data_clean['month_name'] = sales_data_clean['date'].dt.month_name().str[0:3]

    google_weekly = google_search_data_clean.groupby(['claim_id','week_number','year'])['search_volume'].sum().reset_index().sort_values(by=['week_number','year'] ,ascending = [True,True])
    social_media_weekly = social_media_data_clean.groupby(['claim_id','week_number','year'])['total_post'].sum().reset_index().sort_values(by=['week_number','year'] ,ascending = [True,True])
    sales_weekly = sales_data_clean.groupby(['product_id', 'week_number', 'year', 'date'])[
        ['sales_dollars_value', 'sales_units_value', 'sales_lbs_value']
    ].sum().reset_index().sort_values(by=['week_number', 'year'], ascending=[True, True])
    sales_claim_merge = pd.merge(sales_weekly, theme_product_list_clean, on=['product_id'], how= 'inner')
    google_social_merge = google_weekly.merge(social_media_weekly, left_on=['claim_id','week_number','year'], right_on=['claim_id','week_number','year'], how= 'outer')
    google_social_merge.fillna(0, inplace = True)
    merge_abc = sales_claim_merge.merge(google_social_merge, left_on=['claim_id','week_number','year'], right_on=['claim_id','week_number','year'], how= 'outer')
    merge_abc['sales_lbs_value']= np.where(merge_abc['sales_lbs_value'] == 0,0.5,merge_abc['sales_lbs_value'])
    merge_abc = merge_abc[merge_abc['sales_dollars_value']!=0.0]
    merge_abc['per_unit_value'] = merge_abc['sales_dollars_value'] / merge_abc['sales_units_value']
    merge_abc['per_lbs_value'] = merge_abc['sales_dollars_value'] / merge_abc['sales_lbs_value']
    merge_abc['per_unit_weight_lbs'] = merge_abc['sales_lbs_value'] / merge_abc['sales_units_value']
    merge_abc_vendor = pd.merge(merge_abc,product_manufacturer_list_clean,on='product_id',how='inner')
    vendorwise_data = merge_abc_vendor.groupby(['claim_id','week_number','year','date','vendor']).agg({'sales_dollars_value':'sum','sales_units_value':'sum','sales_lbs_value':'sum','search_volume':'mean','total_post':'mean','per_unit_value':'mean','per_lbs_value':'mean','per_unit_weight_lbs':'mean'}).reset_index()
    client_data = vendorwise_data[vendorwise_data['vendor'] == 'A'].sort_values(by='date')
    client_data['month'] = client_data['date'].dt.month

    save_dataset(context, client_data, "processed/FnB/client_data")

    logger.info(f"Saved the client data in processed directory")

    del (
        google_search_data_clean,
        sales_data_clean,
        social_media_data_clean,
        theme_product_list_clean,
        theme_list_clean,
        product_manufacturer_list_clean,
        google_weekly,
        social_media_weekly,
        sales_weekly,
        sales_claim_merge,
        google_social_merge,
        merge_abc,
        merge_abc_vendor,
        vendorwise_data,
        client_data
    )

    gc.collect()
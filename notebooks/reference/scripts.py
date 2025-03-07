"""Module for listing down additional custom functions required for production."""

import numpy as np
import pandas as pd
from scipy.stats import randint
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

class CombinedAttributesAdder(BaseEstimator, TransformerMixin):
    """
    Custom transformer to add derived attributes.

    Attributes
    ----------
    add_bedrooms_per_room : bool, optional
        Whether to include 'bedrooms_per_room' feature.
    """

    def __init__(self, add_bedrooms_per_room=True):
        self.add_bedrooms_per_room = add_bedrooms_per_room

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        rooms_per_household = X[:, 0] / X[:, 3]
        population_per_household = X[:, 2] / X[:, 3]
        if self.add_bedrooms_per_room:
            bedrooms_per_room = X[:, 1] / X[:, 0]
            return np.c_[
                X, rooms_per_household, population_per_household, bedrooms_per_room
            ]
        return np.c_[X, rooms_per_household, population_per_household]
    
    def inverse_transform(self, X):
        """Reverses the transformation by removing the added attributes."""
        if self.add_bedrooms_per_room:
            return X[:, :-3]  # Remove the last 3 columns: rooms_per_household, population_per_household, bedrooms_per_room
        return X[:, :-2]  # Remove the last 2 columns: rooms_per_household, population_per_household
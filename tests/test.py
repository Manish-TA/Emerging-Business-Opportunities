import pytest
import numpy as np
import os
import sys
from sklearn.utils.estimator_checks import check_estimator

production_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "production")
sys.path.insert(0, production_path)
from scripts import CombinedAttributesAdder

@pytest.fixture
def sample_data():
    """Fixture that provides the sample input data for tests."""
    return np.array([[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]], dtype=float)

def test_transform_with_bedrooms(sample_data):
    """Test that the transform method adds the expected derived features when add_bedrooms_per_room=True."""
    transformer = CombinedAttributesAdder(add_bedrooms_per_room=True)
    X_transformed = transformer.transform(sample_data)
    assert X_transformed.shape[1] == 7

def test_inverse_transform_with_bedrooms(sample_data):
    """Test that the inverse_transform method removes the derived features when add_bedrooms_per_room=True."""
    transformer = CombinedAttributesAdder(add_bedrooms_per_room=True)
    X_transformed = transformer.transform(sample_data)
    X_inverted = transformer.inverse_transform(X_transformed)
    assert X_inverted.shape[1] == 4

def test_transform_without_bedrooms(sample_data):
    """Test that the transform method adds the expected derived features when add_bedrooms_per_room=False."""
    transformer = CombinedAttributesAdder(add_bedrooms_per_room=False)
    X_transformed = transformer.transform(sample_data)
    assert X_transformed.shape[1] == 6

def test_inverse_transform_without_bedrooms(sample_data):
    """Test that the inverse_transform method removes the derived features when add_bedrooms_per_room=False."""
    transformer = CombinedAttributesAdder(add_bedrooms_per_room=False)
    X_transformed = transformer.transform(sample_data)
    X_inverted = transformer.inverse_transform(X_transformed)
    assert X_inverted.shape[1] == 4


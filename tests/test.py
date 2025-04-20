import pytest
import numpy as np
import os
import sys
from sklearn.utils.estimator_checks import check_estimator

def test_sales_data_cleaning():
    from pandas.testing import assert_frame_equal
    import numpy as np
    import pandas as pd

    raw_data = pd.read_csv("data/raw/sales_data.csv")

    cleaned = (
        raw_data.copy()
        .astype({"sales_dollars_value": np.int64})
        .assign(system_calendar_key_N=pd.to_datetime(raw_data["system_calendar_key_N"], format='%Y%m%d'))
        .rename(columns={"system_calendar_key_N": "date"})
    )

    assert cleaned["date"].dtype == "datetime64[ns]"
    assert cleaned["sales_dollars_value"].dtype == "int64"


def test_social_media_data_cleaning():
    import pandas as pd
    import numpy as np

    df = pd.read_excel("data/raw/social_media_data.xlsx")
    cleaned = (
        df.replace({'': np.NaN})
        .dropna()
        .astype({'Theme Id': int})
        .assign(published_date=lambda x: pd.to_datetime(x['published_date']))
    )

    assert cleaned["Theme Id"].dtype == "int64"
    assert cleaned["published_date"].dtype == "datetime64[ns]"
    assert cleaned.isnull().sum().sum() == 0

def test_feature_engineering_output_shape():
    import pandas as pd
    import numpy as np

    df = pd.DataFrame({
        "sales_dollars_value": [100, 200, 300],
        "sales_units_value": [2, 4, 6],
        "sales_lbs_value": [10, 20, 30]
    })

    df["per_unit_value"] = df["sales_dollars_value"] / df["sales_units_value"]
    df["per_lbs_value"] = df["sales_dollars_value"] / df["sales_lbs_value"]
    df["per_unit_weight_lbs"] = df["sales_lbs_value"] / df["sales_units_value"]

    assert np.allclose(df["per_unit_value"], [50.0, 50.0, 50.0])
    assert "per_lbs_value" in df.columns
    assert "per_unit_weight_lbs" in df.columns


def test_lag_feature_creation():
    import pandas as pd

    df = pd.DataFrame({
        "search_volume": [100, 200, 300, 400],
        "sales_dollars_value": [10, 20, 30, 40]
    })

    for i in range(1, 3):
        df[f"search_lag_{i}"] = df["search_volume"].shift(i)
        df[f"sales_lag_{i}"] = df["sales_dollars_value"].shift(i)

    lagged = df.dropna()
    assert all(col in lagged.columns for col in ["search_lag_1", "sales_lag_1", "search_lag_2"])
    assert len(lagged) == 2
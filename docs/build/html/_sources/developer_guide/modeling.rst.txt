========
Modeling
========


Approaches
==========

The modeling problem was treated as a **time series regression task** to forecast weekly sales at a claim level. Given the temporal nature of the data and its dependency on historical patterns (lags), **lag-based feature engineering** was performed for each claim individually.

The main approach adopted was:

- **Lag-based feature generation** of key variables like ``sales_dollars_value`` and ``search_volume``, ranging from 1 to 18 weeks.
- **Standard scaling** of features before model training.
- **Linear regression** as the baseline modeling algorithm, trained per-claim using lag features and evaluated using time-series-aware train-test splitting.
- **Model selection** based on best lag (from 2 to 18) by minimizing **Mean Absolute Error (MAE)** on the validation set.

Alternative approaches such as Random Forest or more complex time series models like ARIMA or Prophet were not pursued, given the requirement for interpretability and ease of deployment in a scalable pipeline.

Experimentations
================

High-Level Experiments
----------------------

- Experiments were conducted across 2 to 18 lag values per claim.
- For each lag configuration, the following metrics were computed:

  - **MAE**
  - **MAPE**
  - **MSE**
  - **RMSE**

- The **best lag** was chosen per claim based on the lowest MAE, and summary results were logged in a final report.

Results & Comparisons
---------------------

- Claims with fewer than 100 data points were excluded from modeling to ensure statistical robustness.
- For eligible claims, the model consistently showed low RMSE and MAPE, especially in periods where lagged sales and search signals were strongly predictive.

Interpretations
---------------

- **Lagged ``sales_dollars_value``** and **``search_volume``** were strong predictors of future sales.
- Claims with stable sales patterns showed better prediction accuracy with longer lag structures (e.g., lag 12–18).
- Claims with more volatility benefited from shorter lag structures (e.g., lag 3–6).
- Search and social volume provided incremental lift in predictive performance but were more variable in their contribution across different claims.

Finalized Model
===============

The finalized modeling framework is a **claim-level linear regression model** using:

- Lagged sales and search volume features (lags 1–18)
- Standard scaled inputs
- Time-series-aware training/testing split (70/30)
- Model selection based on lowest MAE

Regression Reports
----------------
- Regression reports were generated for the a test claim, that is claim with claim_id 8:    
  - `Regression Report <../../../../notebooks/reference/reports/regression_linear_model_report.html>`_     

Rationale
---------

- **Scalability**: Model can be applied to each claim independently.
- **Interpretability**: Linear regression allows clear understanding of feature impact.
- **Flexibility**: Supports lag tuning per claim, adapting to different dynamics.

Trade-offs
----------

- Does not capture complex nonlinearities (future scope for tree-based methods).
- Excludes short claims (<100 weeks), which may miss certain niche but important patterns.
- Currently does not consider seasonality or holiday effects explicitly.

Future Scope
------------

- Explore tree-based regressors (Random Forest, XGBoost) with feature importance tracking.
- Incorporate seasonal decomposition and holiday effects.
- Introduce ensemble models combining time series + machine learning predictions.

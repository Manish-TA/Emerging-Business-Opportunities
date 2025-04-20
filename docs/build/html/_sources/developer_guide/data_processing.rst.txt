===============
Data Processing
===============

Data Cleaning
-------------

The data cleaning step is implemented in the ``fetch_clean_fnb_data`` function, which processes raw datasets related to F&B sales, social media, Google search trends, and metadata. Key cleaning operations include:

**Sales Data**:

- Converted ``sales_dollars_value`` to integer.
- Formatted ``system_calendar_key_N`` as datetime and renamed it to ``date``.
- Standardized all column names to snake_case for consistency.

**Social Media Data**:

- Replaced empty strings with ``NaN`` and dropped all missing rows.
- Formatted ``published_date`` to datetime and renamed to ``date``.
- Renamed ``Theme Id`` to ``claim_id``.
- Dropped duplicates.
- Standardized column names.

**Google Search Data**:

- Replaced empty strings with ``NaN``.
- Formatted ``date`` using the ``%d-%m-%Y`` format.
- Renamed ``year_new`` to ``year``.
- Dropped duplicate rows based on ``date``, ``Claim_ID``, and ``platform``.
- Sorted by ``searchVolume`` in descending order.
- Standardized column names.

**Theme Product List & Theme List**:

- Cleaned and standardized column names.
- Replaced empty strings with ``NaN`` (for ``theme_list``).

**Product Manufacturer List**:

- Dropped unnecessary unnamed columns.
- Cleaned and standardized column names.

All cleaned datasets are saved to the ``cleaned/FnB/`` directory using the defined ``context.save_dataset()`` utility. This ensures consistency and readiness for downstream steps like consolidation, feature engineering, and modeling.

Data Consolidation
------------------

Multiple datasets were consolidated to build an enriched, client-specific dataset for modeling. The merging logic was carefully designed to preserve data integrity and temporal alignment while minimizing null values and data leakage risks.

**Sales and Theme-Product Mapping**:

- An inner join was used between weekly sales data and ``theme_product_list_clean`` on the ``product_id`` column.
- This ensured only valid product-theme combinations were retained.

**Google Search & Social Media**:

- Both datasets were aggregated weekly at the claim level (``claim_id``, ``week_number``, ``year``).
- These were merged using a full outer join to retain all entries.
- Missing values were imputed as 0 post-merge using ``fillna(0)``.

**Sales-Claim Merge with Search-Social Data**:

- Merged sales–claim data with the Google-social dataset using a full outer join on ``claim_id``, ``week_number``, and ``year``.
- Post-merge, rows with missing or zero sales volumes were filtered out.

**Sales per Vendor**:

- Merged with ``product_manufacturer_list_clean`` on ``product_id`` using an inner join to associate products with vendors.

**Client-specific Filtering**:

- Filtered for entries only for **Vendor A**, which became the modeling base (``client_data``).

All joins were performed on consistent keys (``product_id``, ``claim_id``, ``week_number``, ``year``). Sorting and groupings were applied post-merge to maintain temporal order for lag-based modeling.

Imputation
----------

Missing value imputation was applied selectively to ensure consistency while preserving meaningful patterns.

- Blank strings (``""``) were replaced with ``NaN`` across all datasets.
- Rows with critical missing values in the social media data were dropped entirely.
- In the Google search dataset, missing values were filled with 0 after merges using ``fillna(0)``.
- Weekly aggregations were handled by assigning default values (e.g., 0 for missing weeks in search volume or social posts).

These steps ensured the merged datasets were consistent and interpretable, especially when aggregating across weeks.

Feature Transformations
------------------------

Standard scaling was applied to numerical features to normalize their distributions.

The following features were standardized:

- ``sales_dollars_value``
- ``sales_units_value``
- ``sales_lbs_value``
- ``per_unit_value``
- ``per_lbs_value``
- ``per_unit_weight_lbs``
- ``search_volume``
- ``total_post``

No additional transformations (e.g., one-hot encoding, PCA, log transform) were applied. Categorical features were not required at this stage.

Feature Engineering
-------------------

The ``transform_features`` function implements full feature engineering by combining cleaned datasets into a unified client-specific view.

**Time-Based Feature Creation**:

- Extracted ``month``, ``month_name``, and ISO ``week_number`` from ``date``.
- Extracted ``year`` for temporal aggregation.

**Weekly Aggregations**:

- **Google Search Data**: Aggregated weekly search volume per ``claim_id`` (sum).
- **Social Media Data**: Aggregated weekly ``total_post`` per ``claim_id`` (sum).
- **Sales Data**: Aggregated weekly per ``product_id``:
  - ``sales_dollars_value``
  - ``sales_units_value``
  - ``sales_lbs_value``

**Derived Metric Engineering**:

- ``per_unit_value``: ``sales_dollars_value`` / ``sales_units_value``
- ``per_lbs_value``: ``sales_dollars_value`` / ``sales_lbs_value`` (0.5 substituted if zero)
- ``per_unit_weight_lbs``: ``sales_lbs_value`` / ``sales_units_value``

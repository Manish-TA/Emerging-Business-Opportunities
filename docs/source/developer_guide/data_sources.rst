============
Data Sources
============

Source ERD
==========

The data is stored in **data/raw/** directory.

It has the following files:

- ``sales_data.csv``  
- ``social_media_data.xlsx``  
- ``google_search_data.csv``  
- ``Theme_list.csv``  
- ``Theme_product_list.csv``  
- ``product_manufacturer_list.csv``  


Source validation rules
=======================

Rules verified on source data include checks on cardinality, key mismatches, and duplicates.  

The reports for the source data can be found in the **notebooks/reference/reports** directory:

- `sales_data <../../../../notebooks/reference/reports/sales_data.html>`_  
- `social_media_data <../../../../notebooks/reference/reports/social_media_data.html>`_  
- `google_search_data <../../../../notebooks/reference/reports/google_search_data.html>`_  
- `Theme_list <../../../../notebooks/reference/reports/Theme_list.html>`_  
- `Theme_product_list <../../../../notebooks/reference/reports/Theme_product_list.html>`_  
- `product_manufacturer_list <../../../../notebooks/reference/reports/product_manufacturer_list.html>`_  


Source data summary
===================

Reports for quick reference covering data preview, variable summaries, and data health are available in the **notebooks/reference/reports** directory:

- `data_exploration_report <../../../../notebooks/reference/reports/data_exploration_report.html>`_  
- `feature_analysis_bivariate <../../../../notebooks/reference/reports/feature_analysis_bivariate.html>`_  
- `feature_analysis_report <../../../../notebooks/reference/reports/feature_analysis_report.html>`_  
- `feature_interaction_report <../../../../notebooks/reference/reports/feature_interaction_report.html>`_  
- `key_drivers_report <../../../../notebooks/reference/reports/key_drivers_report.html>`_  


Configurations
==============

Configuration files, manual inputs, and constants used in the project can be found in:

- ``production/conf/config.yml``

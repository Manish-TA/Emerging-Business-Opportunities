==========
Deployment
==========

The modeling and feature engineering pipeline is integrated with **MLflow** for experiment tracking and reproducibility.

Key deployment steps include:

- **MLflow Integration**:
  
  - Each major step of the pipeline (data cleaning, feature engineering, modeling) is tracked as a separate MLflow run.
  - The entire workflow is launched via a command-line interface using ``cli.py``, ensuring reproducibility and modular execution.
  - Hyperparameters such as lag values, metrics (MAE, MAPE, RMSE), and average predictions are logged to MLflow for each claim-level model.

- **MLflow Server Launch**:
  
  - The MLflow tracking server can be launched locally using:
  
    .. code-block:: bash

        inv launch.tracker-ui

  - This provides a web-based dashboard to explore runs, compare models, and download artifacts.

This setup ensures **full auditability, transparency, and version control** across data, code, and model artifacts throughout the project lifecycle.
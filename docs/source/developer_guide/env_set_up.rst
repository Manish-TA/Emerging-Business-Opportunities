==========================
Environment Setup Guide
==========================

Pre-requisites
=================

1. **Miniconda**  
   Ensure you have **Miniconda** installed and accessible from your shell. If not, download it here: https://docs.conda.io/en/latest/miniconda.html

   .. note::
      If you already have Anaconda installed, you can skip this step.  
      If `conda` is not recognized in the shell, run::

         conda init

2. **Git**  
   Ensure `git` is installed and accessible from your shell.

   .. note::
      If you installed Git Bash or GitHub Desktop, `git` CLI might not be available from your default shell. In that case, add the path to `git.exe` to your system path:

      - ``%LOCALAPPDATA%\Programs\Git\git-bash.exe``
      - ``%LOCALAPPDATA%\GitHubDesktop\app-<ver>\resources\app\git\mingw64\bin\git.exe``

3. **Python Packages (Invoke and PyYAML)**  
   Run the following in your base Conda environment:

   .. code-block:: bash

      (base)$ pip install invoke
      (base)$ pip install pyyaml

Getting Started
===========================

Switch to the root folder (i.e., the folder containing this file).

.. note::

   Make sure there are **no spaces** in the folder path. Environment setup will fail if spaces are present.

To view available automation tasks:

.. code-block:: bash

   (base)~/<proj-folder>$ inv -l

To verify pre-requisites:

.. code-block:: bash

   (base)~/<proj-folder>$ inv debug.check-reqs

No error messages should appear.

Environment Architecture
===========================

The environment is divided into two parts:

1. **Core** (must-have):  
   Installed by default via::

   - `deploy/pip/ct-core-dev.txt`
   - `deploy/conda_envs/ct-core-dev.yml`

2. **Addons** (optional):  
   You can choose from:

   - **formatting**: Code styling tools
   - **documentation**: Docstring and `.rst` documentation generation
   - **testing**: Test automation
   - **jupyter**: Notebook support with enhancements
   - **extras**: Nice-to-have utilities
   - **ts**: Time-series modeling tools
   - **pyspark**: PySpark support

Edit the following files to customize:

- ``deploy/pip/addon-<addon-name>-dev.txt``

.. important::

   Use a **single shared environment file** for your team to ensure consistency.

Recommended Setup (Core + Addons)
==========================================

.. tip::

   Default environment name is ``ta-lib-dev``. You can customize it (e.g., ``env-myproject-prod``) by editing ``ENV_PREFIX`` in `tasks.py`.

To set up the core environment:

.. code-block:: bash

   (base)~/<proj-folder>$ inv dev.setup-env --usecase=<specific-usecase>

This installs the core environment along with project dependencies.

.. note::

   Supported usecases: ``tpo``, ``mmx``, ``ebo``, ``rtm``, ``reco``

Install environment without usecase and specify Python version:

.. code-block:: bash

   (base)~/<proj-folder>$ inv dev.setup-env --python-version=3.9

.. note::

   Supported versions: ``3.8``, ``3.9``, ``3.10`` (default is 3.10)

Activate the environment:

.. code-block:: bash

   (base)~/<proj-folder>$ conda activate ta-lib-dev

Install Invoke and PyYAML again in the new environment:

.. code-block:: bash

   (ta-lib-dev)$ pip install invoke
   (ta-lib-dev)$ pip install pyyaml

Install all addons:

.. code-block:: bash

   (ta-lib-dev)$ inv dev.setup-addon --formatting --jupyter --documentation --testing --extras --ts

Check environment info:

.. code-block:: bash

   (ta-lib-dev)$ inv dev.info

Validate your installation:

.. code-block:: bash

   (ta-lib-dev)$ inv test.val-env --usecase=<specific-usecase>

Validate addon installations:

.. code-block:: bash

   (ta-lib-dev)$ inv test.val-env --formatting --jupyter --documentation --testing --extras --ts --pyspark

Manual Environment Setup
==============================

If the automated setup (`invoke`) fails, use the manual process:

1. **Create Conda Environment**

   .. code-block:: bash

      (base)$ conda create --name <env_name> python=<python_version>

2. **Activate Environment**

   .. code-block:: bash

      (base)$ conda activate <env_name>

3. **Install Core Packages**

   .. code-block:: bash

      (<env_name>)$ pip install -r deploy/pip/ct-core-dev.txt

4. **Install Local Code**

   .. code-block:: bash

      (<env_name>)$ pip install -e .

5. **Install Usecase-specific Packages**

   .. code-block:: bash

      (<env_name>)$ pip install -r deploy/pip/ct-<usecase>-dev.txt

6. **Install Addons (Optional)**

   .. code-block:: bash

      (<env_name>)$ pip install -r deploy/pip/addon-jupyter-dev.txt

Cloud Environment Setup
==============================

If `invoke` is not available in your cloud workspace, follow the manual steps above or refer to:  
**[Cloud Environment Setup Guide](<insert-cloud-guide-link>)**

Launching Jupyter Notebooks
==============================

To start a local Jupyter Lab server:

.. code-block:: bash

   (ta-lib-dev)$ inv launch.jupyterlab

Open your browser and go to: http://localhost:8080

You can view options via help:

.. code-block:: bash

   (ta-lib-dev)$ inv launch.jupyterlab --help

Available options:

- ``--password=<str>``
- ``--env=<str>``
- ``--ip=<str>``
- ``--port=<int>``
- ``--platform=<str>``
- ``--token=<str>``

Frequently Asked Questions
==============================

Refer to the official FAQ for help with code template setup, testing, and adoption across phases:  
**[Code Template FAQ](https://tigeranalytics-code-templates.readthedocs-hosted.com/en/latest/faq.html)**
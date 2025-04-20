========
Tool kit
========

In this section we describe the steps needed for a user to be able to use the tool/dashboard/app end-to-end.

Running and Launching Experiment Tracker
-------------------------------------------

Follow the next sections to setup the environment and come back here to run the experiment.

Launching the MLFlow Server
---------------------------
Run the following command to launch the server to track the experiments::

    inv launch.tracker-ui

Run the Experiments
-------------------
Example usage::

    python production/cli.py job run --job-id data-cleaning

This will run the `data-cleaning` job.

To run all the jobs in one go::

    python production/cli.py job run

The default value for `--job-id` is `all`, so it runs all the jobs defined in the job config.

Go through the regression code template documentation for more clear instructions:  
https://tigeranalytics-code-templates.readthedocs-hosted.com/en/latest/code_templates/project_config.html

Note: `mle-core-dev` is the core env file which we are using.

# Workflow Manager Notebooks

This folder contains Jupyter Notebooks to setup and manage workflows of iprPy calculations. See the associated section below for more details about the included workflow Notebooks and what they do.

## 1. Check Modules.ipynb

The Check Modules Notebook loads iprPy and calls the check_modules() function to test the current status of all included modules.  The output provides details about which modules are currently available.  In particular, the modules that fail import likely raise either

- __ModuleNotFoundError__ if the module has additional Python library requirements that need to be installed.
- __NotImplementedError__ if the module is in development or needs to be updated to current iprPy versions.

## 2. Database Manager.ipynb

The Database Manager Notebook oversees commands related to defining database settings for setting up and performing calculation workflows.  At least one database needs to be defined in order to perform the calculation workflows.  In particular, this Notebook allows for 

- Defining databases,
- Specifying the local run_directories where calculations will be placed/performed,
- Copying/uploading reference records to the databases,
- Checking the number and status of records within a database,
- Cleaning records in a database by resetting any that issued errors, and
- Copying/removing database records.

## 3. Workflow Manager.ipynb

The Workflow Manager Notebook provides a centralized location for preparing and running calculations according to the high-throughput workflow used by the NIST Interatomic Potentials Repository.  It relies on the master prepare operations defined for each calculation style that sets default values for a given calculation.  The code in this Notebook can also be copied to a stand-alone Python script allowing for nearly-automated-prepare to be performed.

## old workflow

The old workflow folder collects files associated with older ways of performing prepare.  These may not work properly with the current version of iprPy and are only retained for now until it is verified that all options are still included.
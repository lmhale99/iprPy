# Workflow Manager Notebooks

This folder contains Jupyter Notebooks to setup and manage workflows of iprPy calculations. See the associated section below for more details about the included workflow Notebooks and what they do.

## 1. Check Modules.ipynb

The Check Modules Notebook loads iprPy and calls the check_modules() function to test the current status of all included modules.  The output provides details about which modules are currently available.  In particular, the modules that fail import likely raise either

- __ModuleNotFoundError__ if the module has additional Python library requirements that need to be installed.
- __NotImplementedError__ if the module is in development or needs to be updated to current iprPy versions.

## 2. Library Manager.ipynb
 
The Library Manager Notebook collects the commands for managing the reference library.  The library is a local copy of records from https://potentials.nist.gov/. iprPy uses the [potentials](https://github.com/usnistgov/potentials) Python package to interact with these records, and as such, all settings and downloaded reference files are common for iprPy, potentials and atomman.

The included tools in this Notebook allow for

- Defining the library settings,
- Downloading reference files from https://potentials.nist.gov/, and
- Downloading additional reference records from [Materials Project](https://materialsproject.org/) and [OQMD](http://oqmd.org/).


## 3. Database Manager.ipynb

The Database Manager Notebook oversees commands related to defining database settings for setting up and performing calculation workflows.  At least one database needs to be defined in order to perform the calculation workflows.  In particular, this Notebook allows for 

- Defining databases,
- Specifying the local run_directories where calculations will be placed/performed,
- Copying/uploading reference records from the library to the databases,
- Checking the number and status of records within a database,
- Cleaning records in a database by resetting any that issued errors, and
- Copying/removing database records.

## 4. Workflow Manager.ipynb

The Workflow Manager Notebook provides a centralized location for preparing and running calculations according to the high-throughput workflow used by the NIST Interatomic Potentials Repository.
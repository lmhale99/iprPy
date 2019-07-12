# Workflow Manager Scripts

This folder contains scripts and functions associated with preparing and running iprPy calculations in a manner consistent with the workflows used by the NIST Interatomic Potentials Repository (IPR).  

## Prepare functions

The workflow_prepare package contains pre-defined prepare functions that

1. Are associated with a specific iprPy calculation.
2. Take names for a pre-set database and run_directory as arguments. 
3. Have a built-in default prepare script that specifies the default parameter values used by IPR.
4. Allow keyword arguments to be passed in that add to or replace parameters in the prepare scripts
5. Calls Database.prepare() with the information in 1-4.

In short, these are useful if you want to run the calculations in exactly the same way (workflow order and calculation parameters) as what is done for the IPR website.  

## multi_runners

This is simply a convenience function that uses the Python multiprocessing module to call for multiple runners to execute on a given database + run_directory. In other words, this function allows for the workflow scripts mentioned below to both prepare and run calculations in a specific order.

## Workflow scripts

The other scripts in this folder are workflows, or portions of workflows, associated with running the calculations in high-throughput.  The scripts are divided up into different branches, but the steps involved in each branch are the same and they access the same prepare functions.

- The __demo__ branch provides a demonstration of the workflow for a small subset of potentials/settings.
- The __single__ branch is designed specifically to streamline the workflow for investigating a single potential.
- The __master__ branch removes the limiters to run across all potentials/settings. Due to the massive number of calculations involved, the master scripts are greatly subdivided and it is assumed that runners will be submitted to queuing systems rather than executed directly.
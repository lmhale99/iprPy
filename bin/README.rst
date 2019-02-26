iprPy bin contents
==================

Files
-----

**iprPy** is the command line script for the framework.  See the package
documentation for more details and a list of the options.

**iprPy_script** and **iprPy_slurm** are basic example bash scripts.  These
allow command line calls to iprPy to be submitted to clusters.

Subdirectories
--------------

**prepare** collects example input scripts that can be called using the iprPy
prepare command line option.

**master_workflow** collects Jupyter Notebooks that serve as workflow
managers for computing the calculations for the Interatomic Potentials
Repository website.  These are focused on performing calculations across all
available interatomic potentials.

**demo_workflow** collects Jupyter Notebooks that serve as workflow
managers for computing the calculations for a single or limited number of
potentials.  Where possible, the demo workflows exactly follow the master
workflows.
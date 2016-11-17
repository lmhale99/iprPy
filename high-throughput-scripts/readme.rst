High-Throughput Scripts
=======================

This folder collects scripts that are used for running the iprPy calculations 
in a high-throughput manner. These are divided into two categories (and 
subdirectories):

1. prepare scripts
2. runner script

prepare
-------

The prepare directory contains Python scripts for preparing calculations. Each
calculation has its own prepare script(s). The initial design was to create one
master prepare.py script capable of handling any of the calculations. This was 
scrapped for being complicated, rigid, and slow.

Following the calculation design, the prepare scripts are executed by feeding 
them an input file containing variable values. Specific information can be 
found with each of the prepare scripts.

runner
------

There is one master runner.py script. All that it needs to operate is an input
file listing the run_directory and lib_directory paths. Examples for the input 
files on different machines and bash scripts for submitting runners to clusters
can be found within.
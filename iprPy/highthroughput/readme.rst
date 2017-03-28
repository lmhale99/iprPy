High-Throughput Scripts
=======================

This folder collects scripts that are used for performing the iprPy calculations 
in a high-throughput manner. These are divided into the following categories (and 
subdirectories):

1. prepare scripts
2. runner script
3. clean script
4. destroy script

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

clean
-----

This script is meant to clean up and reset calculations that failed for reasons
external to the code in the calculation script. To avoid the possibility of 
conflicts, this should ideally only be called on run directories where no 
active runner scripts are currently working. 

Primarily, if a runner script is stopped prematurely, it can leave behind a 
started, but incomplete calculation. This resets the calculations by deleting 
all bid files in the run directory. 

The clean script can also return calculations that issued errors to the run 
directory. This is useful if the error is not due to the calculation itself.

destroy
-------

This is a script for deleting multiple records from a database. As deleting 
records is permanent, care should be used with this script.
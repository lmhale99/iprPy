======
Runner
======

(old...)

Once calculations have been prepared, they can be executed individually or through the use of the runner.py script. All runner.py needs is an input file listing run_directory and lib_directory variables and values. Here are some features of runner:

1. Each instance of runner picks a calculation in run_directory at random and begins to execute it if no other runner has claimed it.
2. Automatically checks if results from another calculation are needed to perform the current calculation. If so, the runner tries to execute the required calculation first. NOTE: the current prepare scripts are NOT supporting this (yet).
3. If a calculation fails, the error message is collected without stopping the runner. 
4. Results or errors are collected and saved into an xml record and saved to the lib_directory record library.
5. The simulation directory is archived as a tar.gz file and moved to the lib_directory.
6. Multiple runners can simultaneously work on calculations in the same run_directory. They can also work on calculations in different run_directories and feed results to the same lib_directory.
7. When submitting on a cluster queue, each runner is assigned a particular number of cores to use. Therefore, running the calculations optimally can be done by collecting the jobs into run_directories based on the number of processors used by the calculation. 
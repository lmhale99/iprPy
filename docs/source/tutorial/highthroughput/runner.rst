======
Runner
======

Introduction
============

Prepared calculations can be systematically executed by starting one or more
runners. Each runner operates over a single run_directory and database.

Starting runners
================
There are multiple ways that a runner can be started.  **Note**: With all of
these methods, do *not* start the runner using an MPI command!  If a
calculation is to use multiprocessing, it should be specified by parameters in
the calculation’s input file.

Runner script
-------------
The runner.py script in the iprPy/highthroughput folder/module can be executed
directly as::

    python runner.py <runner.in>

or::
    
    ./runner.py <runner.in>
    
where <runner.in> is the name/path for an input parameter file used by the
runner. The runner’s input file should only specify a “run_directory” term, a
“database” term and any “database_*” access terms necessary to define the
run_directory and database to interact with.

Inline command
--------------
A runner can be started by entering iprPy’s bin directory and using the inline
terminal command::

    ./iprPy runner <database> <run_directory>
    
where <database> and <run_directory> are the names associated with a database
and a run_directory that have been set using the iprPy set inline command.

Call from Python
----------------

A runner can be started from a Python script or a Jupyter Notebook by
calling::

    iprPy.highthroughput.runner(<dbase>, <run_directory>)
    
where <dbase> is an iprPy.Database object, and <run_directory> is the string
path to the run_directory to use.

Submitting to a queue
---------------------

The bin/ directory of iprPy also contains simple example bash scripts that
can be used for submitting jobs to a queue::

    <submission_command> iprPy_runner <runner.in>

or::

    <submission_command> iprPy_script runner <database> <run_directory>
    
The difference between these two is that iprPy_runner uses the runner.py
script, whereas iprPy_script uses the iprPy inline command. The advantage of
iprPy_script is that it can take advantage of the pre-defined databases and
run_directories, and can be used to submit other high-throughput commands as
jobs.

**Note**: The <submission_command> should specify the number of cores assigned
to the runner. To be most efficient, this should correspond to the number of
cores that the calculation instances in the run_directory will try to use (as
specified in the instances’ input files).

Full process
============

This is a full description of the process that a runner uses:

1. A calculation folder in the run_directory is selected at random.
2. The runner attempts to bid on the calculation instance. This step is done
   to help ensure that only one runner operates on any calculation instance.

    a. If the calculation folder already contains a *.bid file, then the bid
       fails.
    b. The runner creates a *.bid file using the runner’s pid number.
    c. After waiting one second, the runner checks all *.bid files in the
       folder. If the runner’s pid corresponds to the minimum *.bid, then the
       bid succeeds. Otherwise it fails.
       
3. If the bid is successful, it checks all files in the calculation instance’s
   folder. For any XML or JSON records, it checks for a “status” element.

    a. “status” == “not calculated” indicates that a necessary parent
       calculation had not been performed at the time that the current
       calculation instance was prepared. The runner will update the record
       with the database’s copy. If “status” is still “not calculated”, the
       runner will remove its bid from the current calculation instance and
       try to bid on the parent calculation instance.
    b. “status” == “error” indicates that a necessary parent calculation
       failed. The current calculation instance will raise an error to reflect
       this.

4. The calculation instance is checked to ensure that it is valid and
   complete. The folder must contain exactly one each of calc_*.py and
   calc_*.in files, and there must be a corresponding record in the database.
   If not, the calculation instance is moved to an orphan directory.
5. The calculation instance is executed as a subprocess by running the
   identified calc_*.py script and passing it the calc_*.in file and the
   calculation instance’s unique key as arguments.
6. If the calculation successfully finishes, then the generated results.json
   file is uploaded to the database.
7. If the calculation issues an error, then the record for the calculation
   instance is updated by changing “status” to “error” and saving the Python
   error message to an “error” element.
8. The folder for the finished calculation instance is archived as a .tar.gz
   file and uploaded to the database. The calculation instance is deleted from
   the run_directory, with the *.bid file being deleted last to help prevent
   runner collisions.
9. Steps 1-8 are repeated until either the run_directory is empty or the
   runner fails ten bids in a row.

Runner log files
================

When a runner is started, it will create a .log file in the runner-logs/
directory of iprPy. Each runner log file will be uniquely named based on the
date and time that the runner was started. As the runner proceeds, it will
append information to the log file, flushing after each line to ensure that
the log files are up to date. The information listed in the log file includes:

- The key for any calculation instance that the runner succeeds at bidding
  for.
- Information about if any parent records needed to be updated or if any
  parent calculation instances needed to be performed.
- A message if the calculation instance was successful, moved to the orphan
  directory, or issued an error. For the errors, the corresponding Python
  error message is also added.
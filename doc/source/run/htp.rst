=====================================
High-Throughput Calculation Execution
=====================================

Unlike other high-throughput calculation frameworks, iprPy does not require an active server.  This makes it easier to set up iprPy at the cost of some of the higher-level automation tools.

There are five primary steps for performing high-throughput calculations using iprPy:

#. Define a database and a run_directory.  The database stores records, while the run_directory is the path to the local directory where calculation files are placed for execution.

#. Build the database by uploading reference records.

#. Prepare calculations for high-throughput execution.  For every instance of the calculation being prepared, a calculation folder is created in a run directory that contains all necessary files for execution, and a corresponding incomplete record is added to a database.

#. Runners systematically execute all calculations in a run directory and update the calculation records in a database upon completion.

#. Access records from the database to check on the status of the calculations and to analyze results.

These actions can be performed either in Python or by using the iprPy inline commands.  The basic Python functions are described below, while all inline commands are described here.

Define
------

The prepare and runner steps require both information for accessing both a database of records and a local run directory where prepared calculations are placed.  iprPy allows for the access information for both databases and run directories to be saved under simple names.

.. code-block:: python
    
    iprPy.set_database(name='myDB', style='local', host='/users/me/myDB')
    iprPy.set_run_directory(name='myDB_1', path='/users/me/rundirs/myDB/1')

Note that these only have to be done once per database/run_directory as the information is saved to a configuration file.  The information can later be accessed by name

.. code-block:: python
    
    database = iprPy.load_database(name='myDB')
    run_directory = iprPy.load_run_directory(name='myDB_1')

The suggested practice is to set up a run_directory for each unique database and number of computational cores that you plan on using to perform the calculation.  For example, "myDB_1" is the run_directory for single core runs that are stored in the "myDB" database.  See the runner section below for more details.

Build
-----

In order to prepare calculations based on reference records, the information must be uploaded to the database.

.. code-block:: python
    
    database.build_refs()

This will copy all records in the iprPy/library directory to the database.  If you want to upload reference records from a different location, you can pass another directory path in to the function.

Note that buid_refs() only adds missing records to the database and does not update existing records.

Prepare
-------

Multiple instances of a Calculation can be prepared by loading database, run_directory information, selecting a Calculation style, and passing in an input parameter file.  The prepare input parameter file follows a simple format that is similar but not identical to the calculation script input parameter file format.

- The parameters are given in key-value format, with each line listing a parameter followed by its assigned value.

- Any parameters that are not listed or not given values will be ignored and be given default values, if allowed by the calculation.

- Any terms listed after a # will be treated as comments and ignored.

- Some parameters can be assigned multiple values by listing multiple key-value lines for the same key.

- Each key that can be assigned multiple values is part of a set, in which each parameter must have either the same number of assigned values or no assigned values.  When the calculation is prepared, the different multiple value sets will be looped over to build meaningful combinations of input parameters for the calculation script.

The keys that are restricted to single values and the multiple value key sets for a given calculation can be retrieved by loading the calculation in iprPy and accessing the singularkeys and multikeys attributes, respectively.

.. code-block:: python

    calculation = iprPy.load_calculation(calc_style)
    print(calculation.singularkeys)
    for keyset in calculation.multikeys:
        print(keyset)

The prepare input parameter files also support the buildcombos key, which calls predefined functions that assist in generating multi-valued key sets based on available records within the database.  For instance, these make it simple to prepare the same calculation for all LAMMPS potentials that contain an interaction for a specific element, or based on all calculation results of a given calculation style.  See the buildcombos section for more details on all implemented functions.

The calculation can be prepared from Python based on the following example

.. code-block:: python

    database = iprPy.load_database(name='my_DB')
    run_directory = iprPy.load_run_directory(name='myDB_1')
    calculation = iprPy.load_calculation(calc_style)
    
    database.prepare(run_directory, calculation, input_script='prepare.in')

Alternatively, the input terms can be directly passed to database.prepare as keyword arguments of the function.  If this is done, the parameter values must be strings or lists of strings for the allowed multi-valued keys.  

Runner
------

A runner systematically executes all prepared calculations within a specified run_directory and updates the associated record within a database upon completion.  Starting a runner from Python is as simple as

.. code-block:: python

    database.runner(run_directory)

When the runner is started, it does a number of things

1. A calculation folder in the run_directory is selected at random.

2. The runner checks the calculation folder for the following

    A) A .bid file indicates that another runner is already operating on the calculation, and that the runner should pick a new one.
    
    B) Any included .xml and .json files may be results records from a parent calculation.  Their status is checked and updated from the database if needed.  The calculation will be passed over for the time being if any of the parent calculations have not yet been completed.
    
    C) If there is no associated record in the database for the calculation, then the calculation folder is archived to an orphan directory.

3. If the calculation is free and ready, then the runner will create a .bid file and run the calculation.

4. Upon completion, the calculation's record is updated, and the calculation folder is zipped and archived to the database.

5. Steps 1-4 are repeated until either there are no more calculation folders or the runner chooses ten calculation folders in a row that contain a .bid file.

Some things to note about this process

- Multiple runners can operate on the same run_directory at the same time.  The .bid files and the logic around them help avoid any conflicts.

- The checking of the parent calculation status allows for some calculations to be prepared before their parents have been executed.  Note that this currently only works if everything the child calculation needs from the parent calculation can be obtained from the complete parent record.

- If you are working with more than one database, keeping each run_directory associated with a single database helps avoid any issues with the calculations accidentally being moved to the orphan directory (see step 2C).

- If each runner is submitted to a queue that limits the available core resources, then a different run_directory should be defined for each unique number of cores that you want to run calculations for.  This allows for simultaneous execution of heterogeneous calculations while maximizing the work each calculation performs.

- Any calculations that fail to complete due to the runner being prematurely killed will retain .bid files.  These will need to be removed in order for a new runner to restart the calculation.

Access
------

At any time, the status of all calculations of a given style can be checked with the database.check_records() method.  This will print the total number of calculation records for the style, then list how many are complete, still to run, and issued errors.

A single record can be retrieved with the database.get_record() method, and multiple records can be retrieved with database.get_records().  Most of the information can also be retrieved within a spreadsheet-like data frame using the database.get_records_df() method.

The database object also has a few other methods supporting the high-throughput calculations:

- copy_records() allows records to be copied from one database to another.

- clean_records() resets any calculations that issued errors back to a run_directory.  This is useful for debugging.

- destroy_records() permanently deletes all stored calculations of a given style.
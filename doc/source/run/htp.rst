=====================================
High-Throughput Calculation Execution
=====================================

There are five primary steps for performing high-throughput calculations using
iprPy

#. Define one or more databases and run directories.  A database stores
   records, while a run directory is a path to a local directory where
   calculation files are placed for execution.

#. Upload reference records from the iprPy/library to the databases that you
   want to use.

#. Prepare calculations for high-throughput execution.  For every instance of
   a calculation style being prepared, a calculation folder is created in a
   run directory that contains all necessary files for execution, and a
   corresponding incomplete record is added to a database.

#. Start one or more runners to systematically execute the prepared
   calculations in a run directory and update the associated calculation
   records in the database upon completion.

#. Access records from the database to check on the status of the calculations
   and to analyze results.

These actions can be performed either in Python or by using the iprPy inline
commands.  The basic Python functions are described below, while the inline
commands are described on the next documentation page.

Examples and supporting Jupyter Notebooks can be found in the IPR workflow
directory.

Define databases and run directories
------------------------------------

A database can be defined by specifying the database style and any parameters
necessary to interact with the database.  This can be done using
iprPy.load_database().  For example, a local style database can be specified by
providing the local path to where the records are to be located

.. code-block:: python

    import iprPy
    database = iprPy.load_database(style='local', host='/users/me/myDB')

See the documentation for the different database styles to know what parameters
each style accepts.

Rather than having to define a database every time you want to use it, you can
save the access parameters for a database using iprPy.set_database().  The
settings will then be saved and associated with the 'name' parameter that you
give.

.. code-block:: python

    iprPy.set_database(name='myDB', style='local', host='/users/me/myDB')

After a database is set, it can be loaded using its name.

.. code-block:: python

    database = iprPy.load_database(name='myDB')

Warning: the settings are saved in a text configuration file in the same
directory as the iprPy package source code.  Be cautious of saving settings
like passwords if the directory can be accessed by other users.

A run directory is simply a path to a local directory.  Most of the methods
that require a run directory can take a directory path as the argument.  Run
directories can also be saved by name in a fashion similar to how database
settings are saved.  set_run_directory() saves the path, and
load_run_directory() retrieves the path associated with that name.

.. code-block:: python

    iprPy.set_run_directory(name='myDB_1', path='/users/me/rundirs/myDB/1')
    run_directory = iprPy.load_run_directory(name='myDB_1')

Databases and run directories are not inherently connected and can be
independently mixed and swapped.  However, since the calculations that are
prepared within a run directory are tied to records in a database, it is
suggested that each run directory be used with only one database.  One easy way
to do this is to name run directories based on the database name: i.e. the
'myDB_1' run directory has calculations for the 'myDB' database.

Copy references to a database
-----------------------------

Reference records have to be copied to a database before that database can find
and use the records when preparing calculations.  The records in the
iprPy/library directory can easily be added to a database with the build_refs()
method

.. code-block:: python

    database.build_refs()

By default, build_refs will add all records in iprPy/library that are not
already in the database.  See the method's documentation for more options.

Prepare calculations
--------------------

Prepare generates multiple instances of a calculation style based on iterative
combinations of the calculation's input parameters.  It needs to know which
database to place the records in, which calculation style to use, and which
run directory to place the generated calculation instances. Also, the
prepare method needs to know what input parameter values to iterate over, and
which input keys are linked.  The values to iterate over can be specified by
passing prepare either an input file or giving input parameters as keyword
arguments.

.. code-block:: python

    database = iprPy.load_database(name='my_DB')
    run_directory = iprPy.load_run_directory(name='myDB_1')
    calc = iprPy.load_calculation('E_vs_r_scan')

    database.prepare(run_directory, calculation, input_script='prepare.in')

or

.. code-block:: python

    database.prepare(run_directory, calculation, **inputs)

Prepare input file rules
~~~~~~~~~~~~~~~~~~~~~~~~

The input file format used by prepare follows nearly the same rules as the
input file format used to run calculation scripts.  The only real difference is
that keys can be assigned multiple values.

- The parameters are given in key-value format, with each line listing a
  parameter followed by its assigned value.

- Any parameters that are not listed or not given values will be ignored and be
  given default values, if allowed by the calculation.

- Any terms listed after a # will be treated as comments and ignored.

- Keys can be assigned multiple values by listing more than one complete
  non-comment key-value line for that key.

Passing inputs as keyword arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, input values can be defined as keyword arguments of prepare.
This option is convenient for dynamically generating input values.

- The keyword name corresponds to the input key.

- Each input value is given as a string matching how it would appear in the
  input file.  For example, myinput='1 angstrom' corresponds to the input file
  line 'myinput   1 angstrom'.

- Multiple values can be given for an input key by simply assigning it a list
  of string values.

Recognized input keys
~~~~~~~~~~~~~~~~~~~~~

The input parameter keys recognized by prepare, and which keys are allowed to
have multiple values is specific to each calculation style.  The recognized
prepare keys consist of all of the keys that the calculation itself recognizes
along with buildcombos functions and a few special keys for handling copying of
data files.  The full list of supported prepare keys for a calculation can be
found by loading the calculation and checking the allkeys properties.

.. code-block:: python

    calc = iprPy.load_calculation('E_vs_r_scan')
    print(calc.allkeys)

Which keys are limited to single values during prepare, and which ones can
have multiple values can also be viewed using the singularkeys and multikeys
properties.  For multikeys, the keys are collected as sets indicating which
ones are paired and iterated through together.  Each key in a multikeys set
must either have the same number of values or no values assigned to it.

.. code-block:: python

    print(calc.singularkeys)
    for keyset in calc.multikeys:
        print(keyset)

Using buildcombos functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The buildcombos functions are special functions that can be used during prepare
to build values for multikeys sets based on records that exist in the database.
This allows for calculation workflows to be constructed where results for one
calculation can be used as inputs for another.

The buildcombos functions can be used within a prepare input file by starting
an input line with the buildcombos key.  The buildcombos value then consists of
the name of the buildcombos style to use, one of the keys in the keyset
that the buildcombos function will operate on, and an optional name to use for
the buildcombos call.  Additional parameters can then be passed to that
buildcombos function by defining input keys that start with the buildcombos
name and an underscore.

For example, the prepare input lines::

    buildcombos           atomicparent load_file parent
    parent_record_style   relaxed_crystal

will build values for the keyset containing load_file based on the atomic
configuration information stored in relaxed_crystal records.

See the documentation for the buildcombos styles for more details on what each
style does and what parameters it recognizes.

Executing calculations with runners
-----------------------------------

Once calculations are prepared, they can be executed by starting one or more
runners.  A runner systematically executes the prepared calculations within a
specified run_directory and updates the associated record within a database
upon completion.  Starting a runner from Python is as simple as

.. code-block:: python

    database.runner(run_directory)

The runner script has been designed to allow multiple active runners in the
same run directory and some limited workflow support.  So that runners can
recognize which calculations other runners are performing, .bid files are
placed in the calculation folders.  If runners are prematurely stopped, the
.bid files will need to be removed to keep new runners from skipping over the
calculation folders.

If submitting runners to a queue, note that each runner will be limited to a
certain number of cores.  For this reason, it is recommended that calculations
be divided into different run directories based on how many cores you want to
use.

Runner process
~~~~~~~~~~~~~~

This details the specific steps that a runner performs

1. A calculation folder in the run directory is selected at random.

2. The runner checks the calculation folder for the following files

    A) A .bid file indicates that another runner is already operating on the
       calculation, and therefore should be left alone.

    B) Any included .xml and .json files may be results records from a parent
       calculation.  Their status is checked and updated from the database if
       needed.  If a parent record is found to be incomplete, the runner will
       try running the parent calculation.

    C) If the folder is missing either calc\_[style].py or calc\_[style].in, or
       there is no corresponding record in the database, then the calculation
       folder is archived to an orphan directory.

3. If the calculation is free and ready, then the runner will create a .bid
   file and run the calculation.

4. Upon completion, the calculation's record is updated, and the calculation
   folder is zipped and archived to the database.

5. Steps 1-4 are repeated until either there are no more calculation folders
   or the runner fails to find an open calculation after a set number of
   attempts.

Additional tools for database access and manipulation
-----------------------------------------------------

The database object also has additional methods for accessing and manipulating
records

- get_records() retrieves all records matching given criterion.

- get_record() retrieves one record that uniquely matches the given criterion.
  Raises an error if no or multiple matching calculations are found.

- get_records_df() returns record information as a pandas DataFrame.

- get_tar() retrieves the archived calculation folder for a record as a tarfile
  object.

- check_records() will display the number of records in the database for a
  given record style, and for calculation records will count how many are
  finished, still to run, or issued errors.

- copy_records() allows records to be copied from one database to another.

- clean_records() resets any calculations that issued errors back to a
  run_directory and removes .bid files.  This is useful for debugging.

- destroy_records() permanently deletes all stored calculations of a given
  style.

==========================
High Throughput Operations
==========================

Once you have at least one database and run directory defined, you can start performing calculations in high throughput!

1. Database methods
===================

The nature of high throughput calculations involves performing numerous calculations.  This results in the need of a database to help manage the generated results.  As such, the iprPy Databases contain numerous methods for exploring and manipulating records in a database.  This section lists the supported operations both for command line and Python methods

.. code-block:: python

    import iprPy
    db = iprPy.load_database(<database_name>)


1.1. Record query operations
----------------------------

Records in the database can be queried and retrieved in a number of ways.

1.1.1. Command line
```````````````````

.. code-block:: bash

    $iprPy retrieve <database_name> <record_style> <record_name>

will search the database for the indicated record and save a copy to the working directory.  This is useful for fetching any records that may be used as inputs for a calculation.

1.1.2. Python
`````````````

These are the methods of the iprPy Database class associated with basic record interactions and queries
    
- get_records() retrieves all records matching given criterion.

- get_record() retrieves one record that uniquely matches the given criterion.
  Raises an error if no or multiple matching calculations are found.

- get_records_df() finds all records matching the given criterion and returns a pandas.DataFrame containing the record metadata fields

- retrieve_record() retrieves one record that uniquely matches the given criterion and automatically saves a copy of it.

- get_parent_records() looks at the fields in a calculation record and identifies any parent records that were used as inputs.  The parent records are then retrieved from the database.  This can be useful to extract important data from parent records if the information is not copied over to the child records.

- get_tar() retrieves the archived calculation folder for a record as a tarfile
  object.

1.2. Copying records
--------------------

1.2.1. Command line
```````````````````
.. code-block:: bash

    $iprPy copy_records <source> <dest> <record_style> [-n, --notar] [-o, --overwrite]

Copies all records of a given style from the source database name to the dest
database name.  The notar flag indicates that only records and not any tar
blobs are to be copied.  The overwrite flag indicates that all records be copied
over and updated rather than just copying over the missing records.

.. code-block:: bash

    $iprPy copy_references <source> <dest> [-n, --notar] [-o, --overwrite]

Copies all records associated with the reference styles.  This is a convenience
operation for prepping a new database with all of the reference records.  The notar flag
indicates that only records and not any tar blobs are to be copied.  The overwrite flag
indicates that all records be copied over and updated rather than just copying over the
missing records.


1.2.2. Python
`````````````

.. code-block:: python

    db.copy_records(dest, record_style=None, records=None, includetar=True, overwrite=False

Copies records of a given style from the current database object to the dest database.  If record_style is given, then all records of that style are copied over.  Alternatively, a pre-selected list of records can be given to copy over.  includetar indicates if any associated tar archives are also copied over, and overwrite indicates if all records are copied over and updated or only missing records are copied over.

.. code-block:: python

    db.copy_references(dest, includetar=True, overwrite=False)

Copies all records associated with the reference styles.  This is a convenience operation for prepping a new database with all of the reference records.  includetar indicates if any associated tar archives are also copied over, and overwrite indicates if all records are copied over and updated or only missing records are copied over.

.. code-block:: python

    db.merge_records(dest, record_style, includetar=True, overwrite=False, dryrun=False)

This method compares all records of a given style between the two databases before copying.  With includetar=True, the method will search for both missing records and tar files for the record style.  With overwrite=True, the contents of all records in both databases are compared to identify only the ones that have changed.  With dryrun=True, only the comparison operations are performed and the new/different records are returned as a list.  While comparing all records can be slow, it usually saves time overall compared to trying to update all records of the given style.  

1.3. Prepare and run
--------------------

1.3.1. Command line
```````````````````

.. code-block:: bash

    $iprPy prepare <database_name> <run_directory_name> <calculation_style> <input_file>

Prepares a set of calculations associated with the indicated calculation style
based on the indicated input file.  See Section #2 below for more details.

.. code-block:: bash

    $iprPy master_prepare <database_name> <input_file>

Prepares one or more sets of calculations based on the indicated input file.
Multiple calculation styles can be prepared with one script based on starting
with pre-defined settings for that calculation.  See Section #2 below for more
details.

.. code-block:: bash

    $iprPy runner <database_name> <run_directory_name> [-c, --calc_name <calc_name>] [-t, --temp] [-b, --bidtries] [-v, --bidverbose]

Starts a runner script operating on a run directory and uploads results to a
database.  See Section #3 below for more details.

1.3.2. Python
`````````````
.. code-block:: python

    db.prepare(run_directory, calculation, input_script=None, debug=False, **kwargs)

Prepares a set of calculations associated with the indicated calculation style
based on the indicated input file or kwargs given.  See Section #2 below for
more details.

.. code-block:: python

    db.master_prepare(input_script=None, **kwargs)

Prepares one or more sets of calculations based on the indicated input file or kwargs.
Multiple calculation styles can be prepared with one script based on starting
with pre-defined settings for that calculation.  See Section #2 below for more
details.

.. code-block:: python

    db.runner(run_directory, calc_name=None, orphan_directory=None,
              hold_directory=None, log=True, bidtries=10, bidverbose=False,
              temp=False, temp_directory=None)

Starts a runner process operating on a run directory and uploads results to
the database.  See Section #3 below for more details.

.. code-block:: python

    runner = db.runmanager(run_directory, orphan_directory=None,
                           hold_directory=None, log=True)

Creates and returns a RunManager object for the database and run directory.
This gives users more direct control over the order and settings associated
with each calculation being performed.  See Section #3 below for more
details. 


1.4. Utility methods
--------------------

1.4.1. Command line
```````````````````

.. code-block:: bash

    $iprPy check_records <database_name> <record_style>

Queries all records of the specific style and displays how many are found.  If
the record style is associated with a calculation, then it will also display
the number of records for each status value: "finished", "error", and 
"not completed".

.. code-block:: bash

    $iprPy clean_records <database_name> <run_directory_name> <record_style>

This is a utility command that finds all of the calculation records of the
indicated style that issued errors and resets them to a "not calculated" state.
This involves changing the records in the database, extracting the calculation
archives to the run directory, and cleaning out any bid files.  clean_records
is primarily useful for debugging calculations where issues can be fixed in the
code and then the failed runs performed again.

.. code-block:: bash

    $iprPy finish_calculations <database_name> <run_directory_name> [-v, --verbose]

Searches a run directory for calculations that have finished and and generated
a results.json files and uploads them to the database.  Useful if the database
is remote and the connection was lost while the calculations were finishing up.

.. code-block:: bash

    $iprPy reset_orphans <run_directory_name> [<orphan_directory>]

Runners will move any calculations that they find that lack a corresponding
record in the database to an orphan directory.  This occurs if the wrong
database is specified or a connection to a database is lost.  The reset_orphans
command returns the orphaned calculations to a run directory so that they can
be operated on by another runner.  The orphan_directory value is optional if
the runner used the default orphan_directory setting.

.. code-block:: bash

    $iprPy destroy_records <database_name> <record_style>

Permanently deletes all records and any tar archives for the indicated record
style.

1.4.2 Python
````````````
.. code-block:: python

    db.check_records(record_style=None)

Queries all records of the specific style and displays how many are found.  If
the record style is associated with a calculation, then it will also display
the number of records for each status value: "finished", "error", and 
"not completed".

.. code-block:: python

    db.clean_records(run_directory, record_style=None, records=None)

This is a utility command that finds all of the calculation records of the
indicated style that issued errors and resets them to a "not calculated" state.
This involves changing the records in the database, extracting the calculation
archives to the run directory, and cleaning out any bid files.  clean_records
is primarily useful for debugging calculations where issues can be fixed in the
code and then the failed runs performed again.

.. code-block:: python

    db.finish_calculations(run_directory, verbose=False)

Searches a run directory for calculations that have finished and and generated
a results.json files and uploads them to the database.  Useful if the database
is remote and the connection was lost while the calculations were finishing up.

.. code-block:: python

    db.reset_orphans(run_directory, orphan_directory=None)

Runners will move any calculations that they find that lack a corresponding
record in the database to an orphan directory.  This occurs if the wrong
database is specified or a connection to a database is lost.  The reset_orphans
command returns the orphaned calculations to a run directory so that they can
be operated on by another runner.  The orphan_directory value is optional if
the runner used the default orphan_directory setting.

.. code-block:: python

    db.destroy_records(record_style=None, records=None)

Permanently deletes all records and any tar archives for the indicated record
style or the list of records given.

2. Prepare calculations
=======================

2.1. The prepare process
------------------------

Prepare sets up multiple instances of a calculation to be executed based on iterative combinations of input parameters.  The steps performed by prepare are

#. Each prepare action is associated with a database, run directory and calculation style.
#. The calculation instances being prepared are defined by an input script/dict that is similar to the input script/dict that the calculation style uses except that some parameters can be given multiple values.
#. The calculation style's input parameters are grouped into defined parameter sets that indicate all terms in that group should be of the same length and iterated over together.
#. Additionally, "buildcombos" functions can be used to build combinations of inputs based on records currently in the database. 
#. Based on the prepare script and the defined parameter sets, all meaningful combinations of input parameters are iterated over to generate a list of calculation instances.
#. The generated list is then filtered down by removing calculations that are deemed duplicates of existing records or have combinations of inputs that are evaluated as being invalid.
#. All new, valid calculation instances are then "prepared" by creating a folder in the run directory for the instance that contains the appropriate input script and copies of any required files.
#. An incomplete record for each calculation instance is uploaded to the database after the corresponding calculation instance folder is prepared.

These steps allow for a simple means of building numerous calculation instances to run and helps avoid invalid and duplicate calculations from being generated.

2.2. Prepare input script rules
-------------------------------

The input parameter scripts used by prepare are comparable to the input parameter scripts used by the corresponding calculation style.  The main differences being that multiple values of some terms are supported and the addition of buildcombos operations.

- Each line is treated independently and split into white-spaced delimited
  terms.

- Any terms listed after a "#" will be treated as comments and ignored.

- The first term on any given line corresponds to a parameter name, i.e. a key.
  Any other terms following it are interpreted as the value(s) to assign to
  that parameter.

- If only a parameter name appears on a line with no values (i.e. there is only
  one term) then the line is ignored.

- On a per-calculation basis, some parameters can be assigned multiple values.
  These terms that support multiple values are typically grouped into parameter sets.  See Section 2.2.
  for information on seeing how a calculation's input parameters are grouped.

- Multiple values for parameters can be assigned by providing multiple lines
  with value term(s) that start with the same parameter name. 

- Any parameters not assigned values will be given default values if the
  calculation allows it or will issue an error for required parameters.

- All terms in a parameter set are expected to have the same number of values assigned.  The only exception is if a term is to always use its default value, in which case it can be given no values and the default values will be assumed for each combination.  Alternatively, a term can be explicitly stated to use the default value by giving a value of "none".    

- Lines that start with buildcombos indicate that a buildcombos function is to
  be used to generate values for a parameter set based on records in a database.
  See Section 2.3. below for more details. 

In a Python environment, a dict can alternatively be provided to the prepare method.  Each dict value can be a single string value or a list of string values.  Any buildcombos can be specified by adding one or more values to a "buildcombos" element in the dict.

2.3. Recognized input keys
--------------------------

This section describes how users can see how a calculation's input terms are classified and grouped for prepare operations.

2.3.1. Command line
```````````````````

Nothing yet...

2.3.2. Python
`````````````

All input parameter keys recognized by prepare (sans buildcombos) can be viewed with allkeys

.. code-block:: python

    calc = iprPy.load_calculation('E_vs_r_scan')
    print(calc.allkeys)

Note that allkeys can contain additional keys that are not listed in the calculation's template input.  These extra terms provide internal capabilities beyond what can be conveyed in the text-based input scripts.  The most common example is that every "_file" term that gives a file path has a corresponding "_content" term in allkeys that is used to store the file contents after reading it once.   

The input keys that are limited to single values can be viewed with singularkeys.  The parameters that can have multiple values can be viewed with multikeys.  Note that multikeys are separated into different lists that indicate the parameter sets which are iterated over together meaning that all contained values should be of the same length.

.. code-block:: python

    print(calc.singularkeys)
    print(calc.multikeys)


2.4. Using buildcombos functions
--------------------------------

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

For example, the prepare input lines

.. code-block:: text

    buildcombos           atomicparent load_file parent
    parent_record_style   relaxed_crystal

will build values for the keyset containing load_file based on the atomic
configuration information stored in relaxed_crystal records.

See the documentation for the buildcombos styles for more details on what each
style does and what parameters it recognizes.

3. Executing calculations with runners
======================================

3.1. The runner process
-----------------------
 
A runner is tied to a database and operates on the prepared calculations that are found inside a run directory.

Each active runner performs the following steps

#. A calculation folder in the run directory is selected.

#. The runner "bids" on being able to perform the calculation, which creates a .bid file in the calculation folder to indicate to other runners that the calculation is taken.

#. If the folder is missing a calc\_[style].in input parameter file or there is no corresponding record in the database, then the calculation folder is archived to an orphan directory.

#. If the folder contains .json or .xml files, these may be records associated with parent calculations which may not have been finished at the time the calculation folder was prepared.  The runner will check the database for updated versions of these records.  If the parent calculation has since finished successfully, the record file will be updated.  If the parent calculation is still not finished, then the runner will return to step #1 and try selecting the calculation folder for the parent calculation.  

#. The complete and ready to run calculations will then be executed by the runner. 

#. Upon completion (successful or error), the calculation's record will be updated in the database.  The calculation folder will also be archived as a tar.gz file and stored in the database.  The copy of the calculation folder in the run directory will then be deleted.

#. The default nature of the runners is to return to step #1 with a randomly selected calculation folder.  The runner will stop if no calculation folders remain or the bid process fails a set number of times in a row.

3.2. Additional options
-----------------------

There are a number of optional settings that can be specified when starting a runner.

3.2.1. Command line
```````````````````

These are the options that can be specified with the iprPy runner command.

- **-c <calc_name>, --calc_name <calc_name>** Allows for a specific calculation name to be given.  Doing so will cause the runner to automatically select the indicated calculation and not search for any other calculations to run.  This provides a means of defining jobs on a per-calculation basis that target specific prepared calculations.
- **-t, --temp** If given, the calculation folder will be copied to a temp directory and executed from there.  This may be more efficient for some computational resources.  The downside is that any intermediate calculation results will be lost if the runner is stopped before the calculation finishes.
- **-b <bidtries>, --bidtries <bidtries>** The runner will stop if the bid process fails bidtries times in a row.  Changing this value affects the likelihood of a runner finding an open calculation when the number of available jobs is comparable to the number of active runners.  The default value is 10, which seems to work well in most cases.
- **-v or --bidverbose** If given, the screen output and runner log output will include additional details related to the bidding process.

3.2.2. Python
`````````````

These are the optional parameters that the runner method of a database object accepts.

- **calc_name** (*str, optional*)  The name of a specific calculation to run.  Doing so will cause the runner to automatically select the indicated calculation and not search for any other calculations to run.  This provides a means of defining jobs on a per-calculation basis that target specific prepared calculations.
- **orphan_directory** (*path-like object, optional*) The path for the orphan directory where incomplete calculations are moved.  If None (default) then will use 'orphan' at the same level as the run_directory.
- **hold_directory** (*str, optional*) The path for the hold directory where tar archives that failed to be uploaded are moved to.  If None (default) then will use 'hold' at the same level as the run_directory.
- **log** (*bool, optional*) If True (default), the runner will create and save a log file detailing the status of each calculation that it runs.
- **bidtries** (*int, optional*) The runner will stop if it fails on bidding this many times in a row.  This allows for the cleanup of excess competing runners. Default value is 10.
- **bidverbose** (*bool, optional*) If True, info about the calculation bidding process will be printed. Default value is False.
- **temp** (*bool, optional*) If True, a temporary directory will be automatically created and used for this run.
- **temp_directory** (*path-like object, optional*) The path to an existing temporary directory where the calculations are to be copied to and executed there instead of in the run_directory.
 
3.3. Runners as cluster jobs
----------------------------

The iprPy runner command makes it easy to submit runners as jobs on computing clusters.  The two primary methods of specifying runners as jobs are 

- If your cluster allows for large wall times and the calculations you are performing are small, then you can submit jobs for runners operating normally that will iterate over any prepared calculations until finished or they are stopped.  When running in this manner, note that runner jobs that are killed prematurely may leave behind .bid files in the calculation folders that should be removed to make those calculations available to future runners.

- Alternatively, you can give a specific calculation name to each runner.  This then makes the jobs more traditional in that each job will be associated with a single calculation.

Note that some calculations may be able to use multiple cores in their execution.  As a given cluster job is limited to a certain number of available cores, the prepared jobs should be collected in different run directories based on the number of cores to use.  That way the number of cores available to a runner job matches the number of cores you wish to run each calculation with. 

3.4. RunManager
---------------
The runner method is built around a RunManager object, which can alternately be created from a database.  Doing so gives users more direct control over how the calculations are performed.

The important methods and attributes of a RunManager are

- **run_directory**, **orphan_directory**, and **hold_directory** can all be directly set as class attributes.  This makes it possible to change any of these options between calculations.

- **calclist** returns the list of all calculation names in the run directory.

- **run(calc_name, temp=False, temp_directory=None, bidverbose=False)** will select and run a single calculation indicated by name.  If temp=True, a new temp folder will be created and used.  temp_directory allows for an existing temp folder to be used.

- **runall(bidtries=10, temp=False, temp_directory=None, bidverbose=False)** will iteratively run through calculations in the run directory randomly until either no calculations are left or the bid process fails bidtries times in a row.  

====================
Command Line Actions
====================

Most of the high-throughput actions can alternatively be performed at the command line using the iprPy file located in the iprPy/bin directory.  The following examples show the command assuming that the working directory for your terminal is iprPy/bin.

Define
------

Save database access information to a simple name

.. code-block:: bash
    
    ./iprPy set_database <database name>

This will prompt for the database style, host and any other necessary access parameters.

Save run_directory access information to a simple name

.. code-block:: bash
    
    ./iprPy set_run_directory <run_directory name>

This will prompt for the run_directory path.

There are also similar unset_ options that will delete the stored access information.

Build
-----

.. code-block:: bash
    
    ./iprPy build_refs <database name>

Prepare
-------

.. code-block:: bash
    
    ./iprPy prepare <database name> <run_directory name> <calculation name> <input file>
    
Runner
------

.. code-block:: bash
    
    ./iprPy runner <database name> <run_directory name>

Other
-----

check_modules will list all modular class and function styles that were successfully and unsuccessfully imported with iprPy.

.. code-block:: bash
    
    ./iprPy check_modules

check_records will show how many records of a given style are in the database, and how many of each are completed, still to run, and issued errors.

.. code-block:: bash
    
    ./iprPy check_records <database name> <record style>

copy_records will copy records of a given style from one database to another.

.. code-block:: bash
    
    ./iprPy copy_records <database name> <database name> <record style>

clean_records will reset calculations that issued errors by moving them back into the run_directory.

.. code-block:: bash
    
    ./iprPy clean_records <database name> <run_directory name> <record style>

destroy_records will permanently delete all records of a given style from the run_directory.

.. code-block:: bash
    
    ./iprPy destroy_records <database name> <record style>
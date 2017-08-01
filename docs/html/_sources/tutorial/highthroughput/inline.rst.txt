===========================
Other High-Throughput Tools
===========================

There are a few other tools that can be used for assisting in running
calculations in high-throughput.  All except set and unset can be called using
any of the following methods:

- Execute the Python script located in the iprPy/highthroughput directory.
- Use the iprPy inline command. 
- In Python, call the function that is part of the iprPy.highthroughput
  module.

build
=====

The build tool copies all records from a reference library to a specified
database. If the record already exists in the database, it will be skipped.

**build.py input parameters**

- “database” and “database_*” – defines the access terms for a database.
- "lib_directory" – the path to the reference library to use.  If not given
  then the library/ directory of iprPy is used.

**./iprPy build inline arguments**

- database – the name of a database that has been set using the iprPy set
  command.

**iprPy.highthroughput.build function arguments**

- dbase (iprPy.Database) – a database
- lib_directory (str or None, optional) – the path to the reference library
  to use.  If None (default) then the library/ directory of iprPy is used.

check
=====

The check tool checks on the number and status of all records of a given style
in a database.

**check.py input parameters**

- “database” and “database_*” – defines the access terms for a database.
- "record_style" - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**./iprPy check inline arguments**

- database – the name of a database that has been set using the iprPy set
  command.
- record_style - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**iprPy.highthroughput.check function arguments**

- dbase (iprPy.Database) – a database
- record_style (str or None, optional) – the record style to use.  If None
  (default) then a list of all loaded record styles will be printed and the
  user prompted to select one.
  
check_modules
=============

The check_modules tool will print lists of all Record, Calculation, and
Database styles that were successfully and unsuccessfully loaded by iprPy.  A
style that failed to load indicates that an error was raised when trying to
import it.  This means that there either is an issue with the underlying code
or that all requirements for the style are not met.

No arguments or parameters for this tool.

clean
=====

The clean tool resets calculations that issued errors and cleans the prepared
instances within a run_directory so that runners may operate over them again.
In particular:

- Any calculation instances associated with a record style that issued errors
  are extracted from their database archives and returned to a run_directory.
- The "status" field in the associated records are changed from "error" to 
  "not calculated", and the "error" field is deleted.
- All results and bid files for calculation instances in the run_directory are
  deleted.
  
**Note**: To avoid potential runner collisions, don't clean a run_directory
that multiple runners are currently operating on.

**clean.py input parameters**

- “database” and “database_*” – defines the access terms for a database.
- "run_directory" - the path to a run_directory.
- "record_style" - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**./iprPy clean inline arguments**

- database – the name of a database that has been set using the iprPy set
  command.
- "run_directory" - the name of a run_directory that has been set using the
  iprPy set command.
- record_style - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**iprPy.highthroughput.clean function arguments**

- dbase (iprPy.Database) – a database.
- run_directory (str) - the path to a run_directory.
- record_style (str or None, optional) – the record style to use.  If None
  (default) then a list of all loaded record styles will be printed and the
  user prompted to select one.

copy
====

The copy tool will copy all records of a given style from one database to
another.

**copyrecords.py input parameters**

- “database1” and “database1_*” – defines the access terms for a database to
  copy records from.
- “database2” and “database2_*” – defines the access terms for a database to
  copy records to.
- "record_style" - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.
- "includetar" - indicates if the .tar.gz archives associated with the records
  are to be copied as well.  Default value is True.

**./iprPy clean inline arguments**

- database1 – the name of a database that has been set using the iprPy set
  command to copy records from.
- database2 – the name of a database that has been set using the iprPy set
  command to copy records to.
- record_style - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**iprPy.highthroughput.clean function arguments**

- dbase1 (iprPy.Database) – a database to copy records from.
- dbase2 (iprPy.Database) – a database to copy records to.
- record_style (str or None, optional) – the record style to use.  If None
  (default) then a list of all loaded record styles will be printed and the
  user prompted to select one.
- includetar (bool) - indicates if the .tar.gz archives associated with the
  records are to be copied as well.  Default value is True.

destroy
=======

Permanently deletes all records of a given style from a database.  A prompt
will list the number of matching records, ask if you are sure, and require
that you fully type "yes".

**destroy.py input parameters**

- “database” and “database_*” – defines the access terms for a database.
- "record_style" - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**./iprPy destroy inline arguments**

- database – the name of a database that has been set using the iprPy set
  command.
- record_style - the record style to use.  If not given then a list of
  all loaded record styles will be printed and the user prompted to select
  one.

**iprPy.highthroughput.destroy function arguments**

- dbase (iprPy.Database) – a database.
- record_style (str or None, optional) – the record style to use.  If None
  (default) then a list of all loaded record styles will be printed and the
  user prompted to select one.

set
===

Allows for a database or run_directory to be defined for use with the inline
commands for the other high-throughput tools.  If the name is already
associated with a database or run_directory, a prompt will ask if you want to
overwrite the existing values.  The command will prompt the user to enter the
information specific to the object being defined.  This information is saved
to a JSON-formatted file ".iprPy" in the root iprPy directory.

**./iprPy set inline arguments**

- type – specify database or run_directory.
- name - the name to associate with the database or run_directory

unset
=====

Deletes the information associated with a defined database or run_directory.
A prompt will ask if you are sure, in which you must fully type "yes".

**./iprPy set inline arguments**

- type – specify database or run_directory.
- name - the name of the database or run_directory whose definition is to be
  deleted.
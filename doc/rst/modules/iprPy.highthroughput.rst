
iprPy.highthroughput package
****************************


Module contents
===============

**build(dbase, lib_directory=None)**

   Adds reference records from a library to a database.

   :Parameters:
      * **dbase** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database to access.

      * **lib_directory** (*str**, **optional*) -- The directory path
        for the library.  If not given, then it will use the
        iprPy/library directory.

**check(dbase, record_style=None)**

   Counts and checks on the status of records in a database.

   :Parameters:
      * **dbase** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database to access.

      * **record_style** (*str**, **optional*) -- The record style to
        check on.  If not given, then the available record styles will
        be listed and the user prompted to pick one.

**clean(dbase=None, run_directory=None, record_style=None)**

   Resets all records of a given style that issued errors. Useful if
   the errors are due to external conditions.

   :Parameters:
      * **dbase** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database to access.

      * **run_directory** (*str**, **optional*) -- The directory where
        the cleaned calculation instances are to be returned.

      * **record_style** (*str**, **optional*) -- The record style to
        clean.  If not given, then the available record styles will be
        listed and the user prompted to pick one.

**copy(dbase1, dbase2, record_style=None, includetar=True)**

   Copies all records of a given style from one database to another.

   :Parameters:
      * **dbase1** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database to copy from.

      * **dbase2** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database to copy to.

      * **record_style** (*str**, **optional*) -- The record style to
        copy.  If not given, then the available record styles will be
        listed and the user prompted to pick one.

      * **includetar** (*bool**, **optional*) -- If True, the tar
        archives will be copied along with the records. If False, only
        the records will be copied. (Default is True).

**destroy(dbase, record_style=None)**

   Permanently deletes all records of a given style.

   :Parameters:
      * **dbase** (`iprPy.Database <iprPy.rst#iprPy.Database>`_) --
        The database to access.

      * **record_style** (*str**, **optional*) -- The record style to
        delete.  If not given, then the available record styles will
        be listed and the user prompted to pick one.

**get_database(name=None)**

   Loads a pre-defined database from the settings file.

   :Parameters:
      **name** (*str*) -- The name assigned to a pre-defined database.

   :Returns:
      The identified database.

   :Return type:
      `iprPy.Database <iprPy.rst#iprPy.Database>`_

**get_run_directory(name=None)**

   Loads a pre-defined run_directory from the settings file.

   :Parameters:
      **name** (*str*) -- The name assigned to a pre-defined
      run_directory.

   :Returns:
      The path to the identified run_directory.

   :Return type:
      str

**prepare(dbase, run_directory, input_file=None, calc_style=None,
input_dict=None)**

   High-throughput calculation master prepare script

**runner(dbase, run_directory, orphan_directory=None)**

   High-throughput calculation runner

**set_database(name=None, style=None, host=None)**

   Allows for database information to be defined in the settings file.
   Screen prompts will be given to allow any necessary database
   parameters to be entered.

   :Parameters:
      * **name** (*str**, **optional*) -- The name to assign to the
        database. If not given, the user will be prompted to enter
        one.

      * **style** (*str**, **optional*) -- The database style
        associated with the database. If not given, the user will be
        prompted to enter one.

      * **host** (*str**, **optional*) -- The database host (directory
        path or url) where the database is located. If not given, the
        user will be prompted to enter one.

**set_run_directory(name=None, path=None)**

   Allows for run_directory information to be defined in the settings
   file.

   :Parameters:
      * **name** (*str**, **optional*) -- The name to assign to the
        run_directory.  If not given, the user will be prompted to
        enter one.

      * **path** (*str**, **optional*) -- The directory path for the
        run_directory.  If not given, the user will be prompted to
        enter one.

**unset_database(name=None)**

   Deletes the settings for a pre-defined database from the settings
   file.

   :Parameters:
      **name** (*str*) -- The name assigned to a pre-defined database.

**unset_run_directory(name=None)**

   Deletes the settings for a pre-defined run_directory from the
   settings file.

   :Parameters:
      **name** (*str*) -- The name assigned to a pre-defined
      run_directory.

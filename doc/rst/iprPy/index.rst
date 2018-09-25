
iprPy package
*************


Subpackages
===========

* `iprPy.calculation package <calculation.rst>`_
* `iprPy.compatibility package <compatibility.rst>`_
* `iprPy.database package <database.rst>`_
* `iprPy.input package <input.rst>`_
* `iprPy.record package <record.rst>`_
* `iprPy.tools package <tools.rst>`_

Module contents
===============

``rootdir``

   *str* – The absolute path to the iprPy package’s root directory
   used to locate contained data files.

**check_modules()**

   Prints lists of the calculation, record, and database styles that
   were successfully and unsuccessfully loaded when iprPy was
   initialized.

**load_calculation(style)**

**load_database(name=None, style=None, host=None, **kwargs)**

   Loads a database object.  Can be either loaded from stored settings
   or by defining all needed access information.

   :Parameters:
      * **name** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The name assigned to a pre-defined database.
        If given, can be the only parameter.

      * **style** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The database style to use.

      * **host** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The URL/file path where the database is hosted.

      * **kwargs** (`dict
        <https://docs.python.org/3/library/stdtypes.html#dict>`_*,
        **optional*) – Any other keyword parameters defining necessary
        access information. Allowed keywords are database
        style-specific.

   :Returns:
      The database object.

   :Return type:
      Subclass of iprPy.Database

**load_record(style, name=None, content=None)**

**load_run_directory(name=None)**

   Loads a pre-defined run_directory from the settings file.

   :Parameters:
      **name** (`str
      <https://docs.python.org/3/library/stdtypes.html#str>`_) – The
      name assigned to a pre-defined run_directory.

   :Returns:
      The path to the identified run_directory.

   :Return type:
      `str <https://docs.python.org/3/library/stdtypes.html#str>`_

**set_database(name=None, style=None, host=None)**

   Allows for database information to be defined in the settings file.
   Screen prompts will be given to allow any necessary database
   parameters to be entered.

   :Parameters:
      * **name** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The name to assign to the database. If not
        given, the user will be prompted to enter one.

      * **style** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The database style associated with the
        database. If not given, the user will be prompted to enter
        one.

      * **host** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The database host (directory path or url) where
        the database is located. If not given, the user will be
        prompted to enter one.

**set_run_directory(name=None, path=None)**

   Allows for run_directory information to be defined in the settings
   file.

   :Parameters:
      * **name** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The name to assign to the run_directory.  If
        not given, the user will be prompted to enter one.

      * **path** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The directory path for the run_directory.  If
        not given, the user will be prompted to enter one.

**unset_database(name=None)**

   Deletes the settings for a pre-defined database from the settings
   file.

   :Parameters:
      **name** (`str
      <https://docs.python.org/3/library/stdtypes.html#str>`_) – The
      name assigned to a pre-defined database.

**unset_run_directory(name=None)**

   Deletes the settings for a pre-defined run_directory from the
   settings file.

   :Parameters:
      **name** (`str
      <https://docs.python.org/3/library/stdtypes.html#str>`_) – The
      name assigned to a pre-defined run_directory.

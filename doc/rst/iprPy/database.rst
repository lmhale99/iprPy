
iprPy.database package
**********************


Module contents
===============

``loaded``

   *dict* – Dictionary of the derived classes

``databases_dict``

   *dict* – Dictionary of the database styles that successfully
   loaded. The dictionary keys are the database style names, and the
   values are the loaded modules.

**class Database(host)**

   Bases: `object
   <https://docs.python.org/3/library/functions.html#object>`_

   Class for handling different database styles in the same fashion.
   The class defines the common methods and attributes, which are then
   uniquely implemented for each style.  The available styles are
   loaded from the iprPy.databases submodule.

   **add_record(record=None, name=None, style=None, content=None)**

      Adds a new record to the database.  Will issue an error if a
      matching record already exists in the database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The new record
           to add to the database.  If not given, then name, style and
           content are required.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The name to assign to the new record.
           Required if record is not given.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record style for the new record.
           Required if record is not given.

         * **content** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The xml content of the new record.  Required
           if record is not given.

      :Returns:
         Either the given record or a record composed of the name,
         style, and content.

      :Return type:
         iprPy.Record

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If add_record is not defined for database style.

   **add_tar(record=None, name=None, style=None, root_dir=None)**

      Archives and stores a folder associated with a record.  Issues
      an error if exactly one matching record is not found in the
      database, or the associated record already has a tar archive.
      The record’s name must match the name of the directory being
      archived.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The record to
           associate the tar archive with.  If not given, then name
           and/or style necessary to uniquely identify the record are
           needed.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The name to use in uniquely identifying the
           record.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The style to use in uniquely identifying
           the record.

         * **root_dir** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – Specifies the root directory for finding the
           directory to archive. The directory to archive is at
           <root_dir>/<name>.  (Default is to set root_dir to the
           current working directory.)

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If add_tar is not defined for database style.

   **build_refs(lib_directory=None)**

      Adds reference records from a library to a database.

      :Parameters:
         **lib_directory** (`str
         <https://docs.python.org/3/library/stdtypes.html#str>`_*,
         **optional*) – The directory path for the library.  If not
         given, then it will use the iprPy/library directory.

   **check_records(record_style=None)**

      Counts and checks on the status of records in a database.

      :Parameters:
         **record_style** (`str
         <https://docs.python.org/3/library/stdtypes.html#str>`_*,
         **optional*) – The record style to check on.  If not given,
         then the available record styles will be listed and the user
         prompted to pick one.

   **clean_records(run_directory=None, record_style=None)**

      Resets all records of a given style that issued errors. Useful
      if the errors are due to external conditions.

      :Parameters:
         * **run_directory** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The directory where the cleaned calculation
           instances are to be returned.

         * **record_style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record style to clean.  If not given,
           then the available record styles will be listed and the
           user prompted to pick one.

   **copy_records(dbase2, record_style=None, includetar=True)**

      Copies all records of a given style from one database to
      another.

      :Parameters:
         * **dbase2** (*iprPy.Database*) – The database to copy to.

         * **record_style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record style to copy.  If not given,
           then the available record styles will be listed and the
           user prompted to pick one.

         * **includetar** (`bool
           <https://docs.python.org/3/library/functions.html#bool>`_*,
           **optional*) – If True, the tar archives will be copied
           along with the records. If False, only the records will be
           copied. (Default is True).

   **delete_record(record=None, name=None, style=None)**

      Permanently deletes a record from the database.  Will issue an
      error if exactly one matching record is not found in the
      database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The record to
           delete from the database.  If not given, name and/or style
           are needed to uniquely define the record to delete.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The name of the record to delete.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The style of the record to delete.

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If delete_record is not defined for database style.

   **delete_tar(record=None, name=None, style=None)**

      Deletes a tar file from the database.  Issues an error if
      exactly one matching record is not found in the database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The record
           associated with the tar archive to delete.  If not given,
           then name and/or style necessary to uniquely identify the
           record are needed.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The name to use in uniquely identifying the
           record.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The style to use in uniquely identifying
           the record.

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If delete_tar is not defined for database style.

   **destroy_records(record_style=None)**

      Permanently deletes all records of a given style.

      :Parameters:
         **record_style** (`str
         <https://docs.python.org/3/library/stdtypes.html#str>`_*,
         **optional*) – The record style to delete.  If not given,
         then the available record styles will be listed and the user
         prompted to pick one.

   **get_parent_records(record=None, name=None, style=None)**

      Returns all records that are parents to the given one

   **get_record(name=None, style=None, query=None, **kwargs)**

      Returns a single matching record from the database.  Issues an
      error if multiple or no matching records are found.

      :Parameters:
         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record name or id to limit the search
           by.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record style to limit the search by.

      :Returns:
         The single record from the database matching the given
         parameters.

      :Return type:
         iprPy.Record

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If get_record is not defined for database style.

   **get_records(name=None, style=None, query=None, return_df=False,
   **kwargs)**

      Produces a list of all matching records in the database.

      :Parameters:
         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record name or id to limit the search
           by.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The record style to limit the search by.

      :Returns:
         All records from the database matching the given parameters.

      :Return type:
         list of iprPy.Records

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If get_records is not defined for database style.

   **get_records_df(name=None, style=None, query=None, full=True,
   flat=False, **kwargs)**

      Produces a pandas.DataFrame of all matching records in the
      database.

      :Parameters:
         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_) –
           The record style to collect records of.

         * **full** (`bool
           <https://docs.python.org/3/library/functions.html#bool>`_*,
           **optional*) – Flag used by the calculation records.  A
           True value will include terms for both the calculation’s
           input and results, while a value of False will only include
           input terms (Default is True).

         * **flat** (`bool
           <https://docs.python.org/3/library/functions.html#bool>`_*,
           **optional*) – Flag affecting the format of the dictionary
           terms.  If True, the dictionary terms are limited to having
           only str, int, and float values, which is useful for
           comparisons.  If False, the term values can be of any data
           type, which is convenient for analysis. (Default is False).

      :Returns:
         All records from the database of the given record style.

      :Return type:
         pandas.DataFrame

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If get_record is not defined for database style.

   **get_tar(record=None, name=None, style=None, raw=False)**

      Retrives the tar archive associated with a record in the
      database. Issues an error if exactly one matching record is not
      found in the database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The record to
           retrive the associated tar archive for.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The name to use in uniquely identifying the
           record.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The style to use in uniquely identifying
           the record.

         * **raw** (`bool
           <https://docs.python.org/3/library/functions.html#bool>`_*,
           **optional*) – If True, return the archive as raw binary
           content. If False, return as an open tarfile. (Default is
           False)

      :Returns:
         The tar archive as an open tarfile if raw=False, or as a
         binary str if raw=True.

      :Return type:
         `tarfile
         <https://docs.python.org/3/library/tarfile.html#module-tarfile>`_
         or `str
         <https://docs.python.org/3/library/stdtypes.html#str>`_

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If get_tar is not defined for database style.

   ``host``

      *str* – The database’s host.

   **prepare(run_directory, calculation, **kwargs)**

   **runner(run_directory, orphan_directory=None,
   hold_directory=None)**

   **select_record_style()**

      Console prompt for selecting a record_style

   ``style``

      *str* – The database style

   **update_record(record=None, name=None, style=None, content=None)**

      Replaces an existing record with a new record of matching name
      and style, but new content.  Will issue an error if exactly one
      matching record is not found in the databse.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The record with
           new content to update in the database.  If not given,
           content is required along with name and/or style to
           uniquely define a record to update.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The name to uniquely identify the record to
           update.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The style of the record to update.

         * **content** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – The new xml content to use for the record.
           Required if record is not given.

      :Returns:
         Either the given record or a record composed of the name,
         style, and content.

      :Return type:
         iprPy.Record

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If update_record is not defined for database style.

   **update_tar(record=None, name=None, style=None, root_dir=None)**

      Replaces an existing tar archive for a record with a new one.
      Issues an error if exactly one matching record is not found in
      the database. The record’s name must match the name of the
      directory being archived.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) – The record to
           associate the tar archive with.  If not given, then name
           and/or style necessary to uniquely identify the record are
           needed.

         * **name** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The name to use in uniquely identifying the
           record.

         * **style** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – .The style to use in uniquely identifying
           the record.

         * **root_dir** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – Specifies the root directory for finding the
           directory to archive. The directory to archive is at
           <root_dir>/<name>.

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If update_tar is not defined for database style.

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

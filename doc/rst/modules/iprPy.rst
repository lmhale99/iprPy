
iprPy package
*************


Subpackages
===========

* `iprPy.calculations package <iprPy.calculations.rst>`_
* `iprPy.databases package <iprPy.databases.rst>`_
* `iprPy.highthroughput package <iprPy.highthroughput.rst>`_
* `iprPy.input package <iprPy.input.rst>`_
* `iprPy.prepare package <iprPy.prepare.rst>`_
* `iprPy.records package <iprPy.records.rst>`_
* `iprPy.tools package <iprPy.tools.rst>`_

Module contents
===============

``rootdir``

   *str* -- The absolute path to the iprPy package's root directory
   used to locate contained data files.

**class Calculation(style)**

   Bases: ``object``

   Class for handling different calculation styles in the same
   fashion.  The class defines the common methods and attributes,
   which are then uniquely implemented for each style.  The available
   styles are loaded from the iprPy.calculations submodule.

   ``files``

      *iter of str* -- Path to each file required by the calculation.

   **prepare(dbase, run_directory, *args, **kwargs)**

      Calls the calculation's prepare function.

      :Parameters:
         * **dbase** (*iprPy.Database*) -- The database to use with
           preparing instances of the calculation.

         * **run_directory** (*str*) -- The directory path where all
           calculation instances being prepared are to be placed.

         * ***args** -- Any calculation-specific arguments.

         * ****kwargs** -- Any calculation-specific keyword arguments.

      :Raises:
         ``AttributeError`` -- If prepare is not defined for
         calculation style.

   ``prepare_keys``

      *dict* -- lists 'singular' and 'multi' keys used by prepare.

   **process_input(input_dict, UUID=None, build=True)**

      Processes str input parameters, assigns default values if
      needed, and generates new, more complex terms as used by the
      calculation.

      :Parameters:
         * **input_dict** (*dict*) -- Dictionary containing the
           calculation input parameters with string values.  The
           allowed keys depends on the calculation style.

         * **UUID** (*str**, **optional*) -- Unique identifier to use
           for the calculation instance.  If not given and a 'UUID'
           key is not in input_dict, then a random UUID4 hash tag will
           be assigned.

         * **build** (*bool**, **optional*) -- Indicates if all
           complex terms are to be built.  A value of False allows for
           default values to be assigned even if some inputs required
           by the calculation are incomplete. (Default is True.)

      :Raises:
         ``AttributeError`` -- If process_input is not defined for
         calculation style.

   ``style``

      *str* -- The calculation's style.

   ``template``

      *str* -- The template to use for generating calc.in files.

**class Database(style, host, *args, **kwargs)**

   Bases: ``object``

   Class for handling different database styles in the same fashion.
   The class defines the common methods and attributes, which are then
   uniquely implemented for each style.  The available styles are
   loaded from the iprPy.databases submodule.

   **add_record(record=None, name=None, style=None, content=None)**

      Adds a new record to the database.  Will issue an error if a
      matching record already exists in the database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The new record
           to add to the database.  If not given, then name, style and
           content are required.

         * **name** (*str**, **optional*) -- The name to assign to the
           new record.  Required if record is not given.

         * **style** (*str**, **optional*) -- The record style for the
           new record.  Required if record is not given.

         * **content** (*str**, **optional*) -- The xml content of the
           new record.  Required if record is not given.

      :Returns:
         Either the given record or a record composed of the name,
         style, and content.

      :Return type:
         iprPy.Record

      :Raises:
         ``AttributeError`` -- If add_record is not defined for
         database style.

   **add_tar(record=None, name=None, style=None, root_dir=None)**

      Archives and stores a folder associated with a record.  Issues
      an error if exactly one matching record is not found in the
      database, or the associated record already has a tar archive.
      The record's name must match the name of the directory being
      archived.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The record to
           associate the tar archive with.  If not given, then name
           and/or style necessary to uniquely identify the record are
           needed.

         * **name** (*str**, **optional*) -- .The name to use in
           uniquely identifying the record.

         * **style** (*str**, **optional*) -- .The style to use in
           uniquely identifying the record.

         * **root_dir** (*str**, **optional*) -- Specifies the root
           directory for finding the directory to archive. The
           directory to archive is at <root_dir>/<name>.  (Default is
           to set root_dir to the current working directory.)

      :Raises:
         ``AttributeError`` -- If add_tar is not defined for database
         style.

   **delete_record(record=None, name=None, style=None)**

      Permanently deletes a record from the database.  Will issue an
      error if exactly one matching record is not found in the
      database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The record to
           delete from the database.  If not given, name and/or style
           are needed to uniquely define the record to delete.

         * **name** (*str**, **optional*) -- The name of the record to
           delete.

         * **style** (*str**, **optional*) -- The style of the record
           to delete.

      :Raises:
         ``AttributeError`` -- If delete_record is not defined for
         database style.

   **delete_tar(record=None, name=None, style=None)**

      Deletes a tar file from the database.  Issues an error if
      exactly one matching record is not found in the database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The record
           associated with the tar archive to delete.  If not given,
           then name and/or style necessary to uniquely identify the
           record are needed.

         * **name** (*str**, **optional*) -- .The name to use in
           uniquely identifying the record.

         * **style** (*str**, **optional*) -- .The style to use in
           uniquely identifying the record.

      :Raises:
         ``AttributeError`` -- If delete_tar is not defined for
         database style.

   **get_record(name=None, style=None)**

      Returns a single matching record from the database.  Issues an
      error if multiple or no matching records are found.

      :Parameters:
         * **name** (*str**, **optional*) -- The record name or id to
           limit the search by.

         * **style** (*str**, **optional*) -- The record style to
           limit the search by.

      :Returns:
         The single record from the database matching the given
         parameters.

      :Return type:
         iprPy.Record

      :Raises:
         ``AttributeError`` -- If get_record is not defined for
         database style.

   **get_records(name=None, style=None)**

      Produces a list of all matching records in the database.

      :Parameters:
         * **name** (*str**, **optional*) -- The record name or id to
           limit the search by.

         * **style** (*str**, **optional*) -- The record style to
           limit the search by.

      :Returns:
         All records from the database matching the given parameters.

      :Return type:
         list of iprPy.Records

      :Raises:
         ``AttributeError`` -- If get_records is not defined for
         database style.

   **get_records_df(name=None, style=None, full=True, flat=False)**

      Produces a pandas.DataFrame of all matching records in the
      database.

      :Parameters:
         * **style** (*str*) -- The record style to collect records
           of.

         * **full** (*bool**, **optional*) -- Flag used by the
           calculation records.  A True value will include terms for
           both the calculation's input and results, while a value of
           False will only include input terms (Default is True).

         * **flat** (*bool**, **optional*) -- Flag affecting the
           format of the dictionary terms.  If True, the dictionary
           terms are limited to having only str, int, and float
           values, which is useful for comparisons.  If False, the
           term values can be of any data type, which is convenient
           for analysis. (Default is False).

      :Returns:
         All records from the database of the given record style.

      :Return type:
         pandas.DataFrame

   **get_tar(record=None, name=None, style=None, raw=False)**

      Retrives the tar archive associated with a record in the
      database. Issues an error if exactly one matching record is not
      found in the database.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The record to
           retrive the associated tar archive for.

         * **name** (*str**, **optional*) -- .The name to use in
           uniquely identifying the record.

         * **style** (*str**, **optional*) -- .The style to use in
           uniquely identifying the record.

         * **raw** (*bool**, **optional*) -- If True, return the
           archive as raw binary content. If False, return as an open
           tarfile. (Default is False)

      :Returns:
         The tar archive as an open tarfile if raw=False, or as a
         binary str if raw=True.

      :Return type:
         tarfile or str

      :Raises:
         ``AttributeError`` -- If get_tar is not defined for database
         style.

   ``host``

      *str* -- The database's host.

   **iget_records(name=None, style=None)**

      Iterates through matching records in the database.

      :Parameters:
         * **name** (*str**, **optional*) -- The record name or id to
           limit the search by.

         * **style** (*str**, **optional*) -- The record style to
           limit the search by.

      :Yields:
         *iprPy.Record* -- Each record from the database matching the
         given parameters.

      :Raises:
         ``AttributeError`` -- If iget_records is not defined for
         database style.

   ``style``

      *str* -- The database's style.

   **update_record(record=None, name=None, style=None, content=None)**

      Replaces an existing record with a new record of matching name
      and style, but new content.  Will issue an error if exactly one
      matching record is not found in the databse.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The record
           with new content to update in the database.  If not given,
           content is required along with name and/or style to
           uniquely define a record to update.

         * **name** (*str**, **optional*) -- The name to uniquely
           identify the record to update.

         * **style** (*str**, **optional*) -- The style of the record
           to update.

         * **content** (*str**, **optional*) -- The new xml content to
           use for the record.  Required if record is not given.

      :Returns:
         Either the given record or a record composed of the name,
         style, and content.

      :Return type:
         iprPy.Record

      :Raises:
         ``AttributeError`` -- If update_record is not defined for
         database style.

   **update_tar(record=None, name=None, style=None, root_dir=None)**

      Replaces an existing tar archive for a record with a new one.
      Issues an error if exactly one matching record is not found in
      the database. The record's name must match the name of the
      directory being archived.

      :Parameters:
         * **record** (*iprPy.Record**, **optional*) -- The record to
           associate the tar archive with.  If not given, then name
           and/or style necessary to uniquely identify the record are
           needed.

         * **name** (*str**, **optional*) -- .The name to use in
           uniquely identifying the record.

         * **style** (*str**, **optional*) -- .The style to use in
           uniquely identifying the record.

         * **root_dir** (*str**, **optional*) -- Specifies the root
           directory for finding the directory to archive. The
           directory to archive is at <root_dir>/<name>.

      :Raises:
         ``AttributeError`` -- If update_tar is not defined for
         database style.

**class Record(style, name, content)**

   Bases: ``object``

   Class for handling different record styles in the same fashion.
   The class defines the common methods and attributes, which are then
   uniquely implemented for each style.  The available styles are
   loaded from the iprPy.records submodule.

   ``compare_fterms``

      *list of str* -- The default fterms used by isnew() for
      comparisons.

   ``compare_terms``

      *list of str* -- The default terms used by isnew() for
      comparisons.

   ``content``

      *str* -- The record's XML-formatted content. Can be set
      directly.

   **isnew(record_df=None, record_list=None, database=None,
   terms=None, fterms=None, atol=0.0, rtol=1e-08)**

      Checks the record versus a database, list of records, or
      DataFrame of records to see if any records exists with matching
      terms and fterms.

      :Parameters:
         * **record_df** (*pandas.DataFrame**, **optional*) --
           DataFrame to compare record againts.  record_df must be
           built by converting records to dictionaries using
           Record.todict(full=False, flat=True), then converting the
           list of dictionaries to a DataFrame.  Either record_df,
           record_list or database must be given.

         * **record_list** (*list of iprPy.Records**, **optional*) --
           List of Records to compare against.  Either record_df,
           record_list or database must be given.

         * **database** (*iprPy.Database**, **optional*) -- Database
           containing records of record.style to compare against. All
           records of record.style contained in the database will be
           checked.  Either record_df, record_list or database must be
           given.

         * **terms** (*list of str**, **optional*) -- The keys of the
           dictionary produced by Record.todict(full=False, flat=True)
           to check for equivalency, i.e. use == comparisons for terms
           with str and int values. If not given, will use the record
           style's compare_terms.

         * **fterms** (*list of str**, **optional*) -- The keys of the
           dictionary produced by Record.todict(full=False, flat=True)
           to check for approximately equal values, i.e. use
           numpy.isclose() for terms with float values. If not given,
           will use the record style's compare_fterms.

         * **atol** (*float**, **optional*) -- The absolute tolerance
           to use in numpy.isclose() for comparing fterms (Default
           value is 0.0).

         * **rtol** (*float**, **optional*) -- The relative tolerance
           to use in numpy.isclose() for comparing fterms (Default
           value is 1e-8).

      :Returns:
      :Return type:
         bool

      :Raises:
         ``ValueError`` -- If more than one of record_df, record_list,
         and database are given.

   ``name``

      *str* -- The records's name.

   ``schema``

      *str* -- The absolute directory path to the .xsd file associated
      with the record style.

   ``style``

      *str* -- The records's style.

   **todict(full=True, flat=False)**

      Converts the XML content to a dictionary.

      :Parameters:
         * **full** (*bool**, **optional*) -- Flag used by the
           calculation records.  A True value will include terms for
           both the calculation's input and results, while a value of
           False will only include input terms (Default is True).

         * **flat** (*bool**, **optional*) -- Flag affecting the
           format of the dictionary terms.  If True, the dictionary
           terms are limited to having only str, int, and float
           values, which is useful for comparisons.  If False, the
           term values can be of any data type, which is convenient
           for analysis. (Default is False).

      :Returns:
         A dictionary representation of the record's content.

      :Return type:
         dict

      :Raises:
         ``AttributeError`` -- If todict is not defined for record
         style.

**buildmodel(style, script, input_dict, results_dict=None)**

   Builds a data model of the specified record style based on input
   (and results) parameters.

   :Parameters:
      * **style** (*str*) -- The record style to use.

      * **script** (*str*) -- The name of the calculation script used.

      * **input_dict** (*dict*) -- Dictionary of all input parameter
        terms.

      * **results_dict** (*dict**, **optional*) -- Dictionary
        containing any results produced by the calculation.

   :Returns:
      Data model consistent with the record's schema format.

   :Return type:
      DataModelDict

   :Raises:
      * ``KeyError`` -- If the record style is not available.

      * ``AttributeError`` -- If buildmodel is not defined for record
        style.

**calculation_styles()**

   :Returns:
      All calculation styles successfully loaded.

   :Return type:
      list of str

**check_modules()**

   Prints lists of the calculation, record, and database styles that
   were sucessfully and unsucessfully loaded when iprPy was
   initialized.

**database_fromdict(input_dict, database_key='database')**

   Initializes a Database object based on 'database_*' terms contained
   within a dictionary.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary of input parameter terms
        including 'database' and any other necessary 'database_*' keys
        to fully initialize a Database object.

      * **database_key** (*str**, **optional*) -- Defines the base
        string for identifying the database keys.  Useful if multiple
        database definitions are needed.  (Default is 'database').

   :Returns:
      Database object initialized from input_dict database keys.

   :Return type:
      iprPy.Database

**database_styles()**

   :Returns:
      All database styles successfully loaded.

   :Return type:
      list of str

**record_styles()**

   :Returns:
      All record styles successfully loaded.

   :Return type:
      list of str

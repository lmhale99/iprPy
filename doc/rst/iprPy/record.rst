
iprPy.record package
********************


Module contents
===============

``loaded``

   *dict* – Dictionary of the derived classes

``databases_dict``

   *dict* – Dictionary of the database styles that successfully
   loaded. The dictionary keys are the database style names, and the
   values are the loaded modules.

**class Record(name=None, content=None)**

   Bases: `object
   <https://docs.python.org/3/library/functions.html#object>`_

   Class for handling different record styles in the same fashion.
   The class defines the common methods and attributes, which are then
   uniquely implemented for each style.  The available styles are
   loaded from the iprPy.records submodule.

   **buildcontent(script, input_dict, results_dict=None)**

      Builds a data model of the specified record style based on input
      (and results) parameters.

      :Parameters:
         * **script** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_) –
           The name of the calculation script used.

         * **input_dict** (`dict
           <https://docs.python.org/3/library/stdtypes.html#dict>`_) –
           Dictionary of all input parameter terms.

         * **results_dict** (`dict
           <https://docs.python.org/3/library/stdtypes.html#dict>`_*,
           **optional*) – Dictionary containing any results produced
           by the calculation.

      :Returns:
         Data model consistent with the record’s schema format.

      :Return type:
         DataModelDict

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If buildcontent is not defined for record style.

   ``compare_fterms``

      *list of str* – The default fterms used by isnew() for
      comparisons.

   ``compare_terms``

      *list of str* – The default terms used by isnew() for
      comparisons.

   ``content``

      *DataModelDict* – The record’s content.

   ``contentroot``

      *str* – The root element of the content

   ``directory``

      *str* – The path to the record’s directory

   **isnew(record_df=None, record_list=None, database=None,
   terms=None, fterms=None, atol=0.0, rtol=1e-08)**

      Checks the record versus a database, list of records, or
      DataFrame of records to see if any records exists with matching
      terms and fterms.

      :Parameters:
         * **record_df** (*pandas.DataFrame**, **optional*) –
           DataFrame to compare record againts.  record_df must be
           built by converting records to dictionaries using
           Record.todict(full=False, flat=True), then converting the
           list of dictionaries to a DataFrame.  Either record_df,
           record_list or database must be given.

         * **record_list** (*list of iprPy.Records**, **optional*) –
           List of Records to compare against.  Either record_df,
           record_list or database must be given.

         * **database** (*iprPy.Database**, **optional*) – Database
           containing records of record.style to compare against. All
           records of record.style contained in the database will be
           checked.  Either record_df, record_list or database must be
           given.

         * **terms** (*list of str**, **optional*) – The keys of the
           dictionary produced by Record.todict(full=False, flat=True)
           to check for equivalency, i.e. use == comparisons for terms
           with str and int values. If not given, will use the record
           style’s compare_terms.

         * **fterms** (*list of str**, **optional*) – The keys of the
           dictionary produced by Record.todict(full=False, flat=True)
           to check for approximately equal values, i.e. use
           numpy.isclose() for terms with float values. If not given,
           will use the record style’s compare_fterms.

         * **atol** (`float
           <https://docs.python.org/3/library/functions.html#float>`_*,
           **optional*) – The absolute tolerance to use in
           numpy.isclose() for comparing fterms (Default value is
           0.0).

         * **rtol** (`float
           <https://docs.python.org/3/library/functions.html#float>`_*,
           **optional*) – The relative tolerance to use in
           numpy.isclose() for comparing fterms (Default value is
           1e-8).

      :Returns:
      :Return type:
         `bool
         <https://docs.python.org/3/library/functions.html#bool>`_

      :Raises:
         `ValueError
         <https://docs.python.org/3/library/exceptions.html#ValueError>`_
         – If more than one of record_df, record_list, and database
         are given.

   **isvalid()**

      Looks at the values of elements in the record to determine if
      the associated calculation would be a valid one to run.

      :Returns:
         True if element combinations are valid, False if not.

      :Return type:
         `bool
         <https://docs.python.org/3/library/functions.html#bool>`_

   **match_df(record_df=None, record_list=None, database=None,
   terms=None, fterms=None, atol=0.0, rtol=1e-08)**

      Checks the record versus a database, list of records, or
      DataFrame of records to see if any records exists with matching
      terms and fterms.

      :Parameters:
         * **record_df** (*pandas.DataFrame**, **optional*) –
           DataFrame to compare record againts.  record_df must be
           built by converting records to dictionaries using
           Record.todict(full=False, flat=True), then converting the
           list of dictionaries to a DataFrame.  Either record_df,
           record_list or database must be given.

         * **record_list** (*list of iprPy.Records**, **optional*) –
           List of Records to compare against.  Either record_df,
           record_list or database must be given.

         * **database** (*iprPy.Database**, **optional*) – Database
           containing records of record.style to compare against. All
           records of record.style contained in the database will be
           checked.  Either record_df, record_list or database must be
           given.

         * **terms** (*list of str**, **optional*) – The keys of the
           dictionary produced by Record.todict(full=False, flat=True)
           to check for equivalency, i.e. use == comparisons for terms
           with str and int values. If not given, will use the record
           style’s compare_terms.

         * **fterms** (*list of str**, **optional*) – The keys of the
           dictionary produced by Record.todict(full=False, flat=True)
           to check for approximately equal values, i.e. use
           numpy.isclose() for terms with float values. If not given,
           will use the record style’s compare_fterms.

         * **atol** (`float
           <https://docs.python.org/3/library/functions.html#float>`_*,
           **optional*) – The absolute tolerance to use in
           numpy.isclose() for comparing fterms (Default value is
           0.0).

         * **rtol** (`float
           <https://docs.python.org/3/library/functions.html#float>`_*,
           **optional*) – The relative tolerance to use in
           numpy.isclose() for comparing fterms (Default value is
           1e-8).

      :Returns:
      :Return type:
         `bool
         <https://docs.python.org/3/library/functions.html#bool>`_

      :Raises:
         `ValueError
         <https://docs.python.org/3/library/exceptions.html#ValueError>`_
         – If more than one of record_df, record_list, and database
         are given.

   ``name``

      *str* – The record’s name.

   ``schema``

      *str* – The absolute directory path to the .xsd file associated
      with the record style.

   ``style``

      *str* – The record style

   **todict(full=True, flat=False)**

      Converts the structured content to a simpler dictionary.

      :Parameters:
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
         A dictionary representation of the record’s content.

      :Return type:
         `dict
         <https://docs.python.org/3/library/stdtypes.html#dict>`_

      :Raises:
         `AttributeError
         <https://docs.python.org/3/library/exceptions.html#AttributeError>`_
         – If todict is not defined for record style.

**load_record(style, name=None, content=None)**

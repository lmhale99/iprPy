
iprPy.tools package
*******************


Module contents
===============

**aslist(term)**

   Create list representation of term. Treats a str, unicode term as a
   single item.

   :Parameters:
      **term** (`any
      <https://docs.python.org/3/library/functions.html#any>`_) – Term
      to convert into a list, if needed.

   :Returns:
      All items in term as a list

   :Return type:
      list of any

**dynamic_import(module_file, module_name, ignorelist=[])**

   Dynamically imports classes stored in submodules and makes them
   directly accessible by style name within the returned loaded
   dictionary.

   :Returns:
      * **loaded** (*dict*) – Contains the derived classes that were
        successfully loaded and accessible by style name (root
        submodule).

      * **failed** (*dict*)

**filltemplate(template, variable, s_delimiter, e_delimiter)**

   Takes a template and fills in values for delimited template
   variables.

   :Parameters:
      * **template** (`string
        <https://docs.python.org/3/library/string.html#module-string>`_*
        or **file-like object*) – The template file or file content to
        fill in.

      * **variable** (`dict
        <https://docs.python.org/3/library/stdtypes.html#dict>`_) –
        Dictionary with keys defining the delimited template variable
        terms, and values the values to replace the variable terms
        with.

      * **s_delimiter** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_) – The
        leading delimiter for identifying the template variable terms.

      * **e_delimiter** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_) – The
        trailing delimiter for identifying the template variable
        terms.

   :Returns:
      The template with all delimited variable terms replaced with
      their corresponding defined values from variable.

   :Return type:
      `str <https://docs.python.org/3/library/stdtypes.html#str>`_

   :Raises:
      * `KeyError
        <https://docs.python.org/3/library/exceptions.html#KeyError>`_
        – If delimited term found in template that has no value in
        variable.

      * `ValueError
        <https://docs.python.org/3/library/exceptions.html#ValueError>`_
        – If parsing of s_delimiter, e_delimiter pairs fails.

**iaslist(term)**

   Iterate over items in term as if term was a list. Treats a str,
   unicode term as a single item.

   :Parameters:
      **term** (`any
      <https://docs.python.org/3/library/functions.html#any>`_) – Term
      to iterate over.

   :Yields:
      *any* – Items in the list representation of term.

**screen_input(prompt='')**

   Replacement input function that is compatible with Python versions
   2 and 3, as well as the mingw terminal.

   :Parameters:
      **prompt** (`str
      <https://docs.python.org/3/library/stdtypes.html#str>`_*,
      **optional*) – The screen prompt to use for asking for the
      input.

   :Returns:
      The user input.

   :Return type:
      `str <https://docs.python.org/3/library/stdtypes.html#str>`_

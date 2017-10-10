
iprPy.tools package
*******************


Module contents
===============

**aslist(term)**

   Create list representation of term. Treats a str, unicode term as a
   single item.

   :Parameters:
      **term** (*any*) -- Term to convert into a list, if needed.

   :Returns:
      All items in term as a list

   :Return type:
      list of any

**check_lammps_version(lammps_command)**

   Gets the LAMMPS version and date information by testing
   lammps_command.

   :Parameters:
      **lammps_command** (*str*) -- The LAMMPS executable to get the
      version for.

   :Returns:
      **version_info** -- Dictionary containing 'lammps_version', the
      str LAMMPS version, and 'lammps_date', the corresponding
      datetime.date for the LAMMPS version.

   :Return type:
      dict

   :Raises:
      ``ValueError`` -- If lammps fails to run

**filltemplate(template, variable, s_delimiter, e_delimiter)**

   Takes a template and fills in values for delimited template
   variables.

   :Parameters:
      * **template** (*string** or **file-like object*) -- The
        template file or file content to fill in.

      * **variable** (*dict*) -- Dictionary with keys defining the
        delimited template variable terms, and values the values to
        replace the variable terms with.

      * **s_delimiter** (*str*) -- The leading delimiter for
        identifying the template variable terms.

      * **e_delimiter** (*str*) -- The trailing delimiter for
        identifying the template variable terms.

   :Returns:
      The template with all delimited variable terms replaced with
      their corresponding defined values from variable.

   :Return type:
      str

   :Raises:
      * ``KeyError`` -- If delimited term found in template that has
        no value in variable.

      * ``ValueError`` -- If parsing of s_delimiter, e_delimiter pairs
        fails.

**iaslist(term)**

   Iterate over items in term as if term was a list. Treats a str,
   unicode term as a single item.

   :Parameters:
      **term** (*any*) -- Term to iterate over.

   :Yields:
      *any* -- Items in the list representation of term.

**parseinput(infile, singularkeys=[], allsingular=False)**

   Parses an input file and returns a dictionary of parameter terms.

   These are the parsing rules:

   * The first word in a line is taken as the key name of the
     parameter.

   * All other words are joined together into a single string value
     for the parameter.

   * Words that start with # indicate comments with that word and all
     words to the right of it in the same line being ignored.

   * Any lines with less than two non-comment terms are ignored. In
     other words, blank lines and lines with keys but not values are
     skipped over.

   * Multiple values can be assigned to the same term by repeating the
     key name on a different line.

   * The keyword arguments can be used to issue an error if multiple
     values are trying to be assigned to terms that should only have a
     single values.

   :Parameters:
      * **infile** (*string** or **file-like-object*) -- The file or
        file contents to parse out parameter terms.

      * **singularkeys** (*list of str**, **optional*) -- List of term
        keys that should not have multiple values.

      * **allsingular** (*bool**, **optional*) -- Indicates if all
        term keys should be singular (Default is False).

   :Returns:
      **params** -- Dictionary of parsed input key-value pairs

   :Return type:
      dict

   :Raises:
      ``ValueError`` -- If both singularkeys and allsingular are
      given, or if multiple values found for a singular key.

**screen_input(prompt='')**

   Replacement input function that is compatible with Python versions
   2 and 3, as well as the mingw terminal.

   :Parameters:
      **prompt** (*str**, **optional*) -- The screen prompt to use for
      asking for the input.

   :Returns:
      The user input.

   :Return type:
      str

**termtodict(term, keys)**

   Takes a str term and parses it into a dictionary of key-value pairs
   based on the supplied key list.

   :Parameters:
      * **term** (*str**, **unicode*) -- The str term to parse.

      * **keys** (*list of str*) -- The list of keys to parse by.

   :Returns:
      Dictionary of parsed key-value terms.

   :Return type:
      dict

   :Raises:
      ``ValueError`` -- If any key appears mupltiple times or the
      first word in term does not match a key.

=============================
Adding new buildcombos styles
=============================

The basic steps associated with implementing a new buildcombos style in iprPy
are

#. Create a Python script in the iprPy/input/buildcombos_functions directory.
The file's name will be the buildcombos style name.

#. In the Python file, define a function named for the style.

#. Set \_\_all\_\_ to equal a list containing the function name.

The defined buildcombos function should follow a few basic rules

- The function takes as parameters

    - database: the database used by prepare.

    - keys: the list of keys in the multikeys set that the function builds
      values for.

    - content_dict: a dictionary for storing loaded file content where the
      keys detail the file's name (and type) and the values are the file's
      content.

    - Any other style-specific keyword parameters.  Typically, these are
      related to specifying which database records to use in building the input
      combinations.

- A dictionary 'inputs' is created with keys matching the values in the keys
  list given as a function parameter.

- Records are retrieved from the database and used to generate values for the
  inputs dictionary.  In generating the values, each input key must be assigned
  an equal number of values.  Empty string values can be used to indicate that
  the default calculation values for that term are to be used.

- If any of the inputs keys point to a file that may be used by multiple
  prepared calculations, the file's contents can be loaded and stored in
  content_dict.  This saves time during prepare as files that are reused only
  need to be loaded once.

- The function returns inputs and content_dict.

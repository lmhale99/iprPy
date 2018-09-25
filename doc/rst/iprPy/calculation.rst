
iprPy.calculation package
*************************


Module contents
===============

``loaded``

   *dict* – Dictionary of the derived classes

``databases_dict``

   *dict* – Dictionary of the database styles that successfully
   loaded. The dictionary keys are the database style names, and the
   values are the loaded modules.

**class Calculation**

   Bases: `object
   <https://docs.python.org/3/library/functions.html#object>`_

   Class for handling different calculation styles in the same
   fashion.  The class defines the common methods and attributes,
   which are then uniquely implemented for each style.  The available
   styles are loaded from the iprPy.calculations submodule.

   ``allkeys``

      *list* – All keys used by the calculation.

   **calc(*args, **kwargs)**

      Calls the primary calculation function(s). This needs to be
      defined for each calculation.

   ``directory``

      *str* – The path to the calculation’s directory

   ``files``

      *iter of str* – Path to each file required by the calculation.

   **main(*args)**

      Calls the calculation’s main function.

   ``multikeys``

      *list* – Calculation keys that can have multiple values during
      prepare.

   **process_input(input_dict, UUID=None, build=True)**

      Processes str input parameters, assigns default values if
      needed, and generates new, more complex terms as used by the
      calculation.

      :Parameters:
         * **input_dict** (`dict
           <https://docs.python.org/3/library/stdtypes.html#dict>`_) –
           Dictionary containing the calculation input parameters with
           string values.  The allowed keys depends on the calculation
           style.

         * **UUID** (`str
           <https://docs.python.org/3/library/stdtypes.html#str>`_*,
           **optional*) – Unique identifier to use for the calculation
           instance.  If not given and a ‘UUID’ key is not in
           input_dict, then a random UUID4 hash tag will be assigned.

         * **build** (`bool
           <https://docs.python.org/3/library/functions.html#bool>`_*,
           **optional*) – Indicates if all complex terms are to be
           built.  A value of False allows for default values to be
           assigned even if some inputs required by the calculation
           are incomplete. (Default is True.)

   ``record_style``

      *str* – The record style associated with the calculation.

   ``singularkeys``

      *list* – Calculation keys that can have single values during
      prepare.

   ``style``

      *str* – The calculation style

   ``template``

      *str* – The template to use for generating calc.in files.

**load_calculation(style)**

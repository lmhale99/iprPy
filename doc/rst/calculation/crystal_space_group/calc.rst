
calc_crystal_space_group.py
***************************


Calculation script functions
============================

**crystal_space_group(system, symprec=1e-05, to_primitive=False,
no_idealize=False)**

   Uses spglib to evaluate space group information for a given system.

   :Parameters:
      * **system** (*atomman.System*) – The system to analyze.

      * **symprec** (`float
        <https://docs.python.org/3/library/functions.html#float>`_) –
        Absolute length tolerance to use in identifying symmetry of
        atomic sites and system boundaries.

      * **to_primitive** (`bool
        <https://docs.python.org/3/library/functions.html#bool>`_) –
        Indicates if the returned unit cell is conventional (False) or
        primitive (True). Default value is False.

      * **no_idealize** (`bool
        <https://docs.python.org/3/library/functions.html#bool>`_) –
        Indicates if the atom positions in the returned unit cell are
        averaged (True) or idealized based on the structure (False).
        Default value is False.

   :Returns:
      Results dictionary containing space group information and an
      associated unit cell system.

   :Return type:
      `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_

**main(*args)**

   Main function called when script is executed directly.

**process_input(input_dict, UUID=None, build=True)**

   Processes str input parameters, assigns default values if needed,
   and generates new, more complex terms as used by the calculation.

   :Parameters:
      * **input_dict** (`dict
        <https://docs.python.org/3/library/stdtypes.html#dict>`_) –
        Dictionary containing the calculation input parameters with
        string values.  The allowed keys depends on the calculation
        style.

      * **UUID** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – Unique identifier to use for the calculation
        instance.  If not given and a ‘UUID’ key is not in input_dict,
        then a random UUID4 hash tag will be assigned.

      * **build** (`bool
        <https://docs.python.org/3/library/functions.html#bool>`_*,
        **optional*) – Indicates if all complex terms are to be built.
        A value of False allows for default values to be assigned even
        if some inputs required by the calculation are incomplete.
        (Default is True.)

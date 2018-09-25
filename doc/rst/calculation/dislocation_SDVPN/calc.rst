
calc_dislocation_SDVPN.py
*************************


Calculation script functions
============================

**main(*args)**

   Main function called when script is executed directly.

**peierlsnabarro(alat, C, axes, burgers, gamma, m=[0, 1, 0], n=[0, 0,
1], cutofflongrange=1000.0, tau=array([[0., 0., 0.],        [0., 0.,
0.],        [0., 0., 0.]]), alpha=[0.0], beta=array([[0., 0., 0.],
[0., 0., 0.],        [0., 0., 0.]]), cdiffelastic=False,
cdiffsurface=True, cdiffstress=False, fullstress=True, halfwidth=1.0,
normalizedisreg=True, xnum=None, xmax=None, xstep=None,
min_method='Powell', min_options={}, min_cycles=10)**

   Solves a Peierls-Nabarro dislocation model.

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

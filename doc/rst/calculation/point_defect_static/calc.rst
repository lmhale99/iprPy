
calc_point_defect_static.py
***************************


Calculation script functions
============================

**check_ptd_config(system, point_kwargs, cutoff, tol=1e-05)**

   Evaluates a relaxed system containing a point defect to determine
   if the defect structure has transformed to a different
   configuration.

   :Parameters:
      * **system** (*atomman.System*) – The relaxed defect system.

      * **point_kwargs** (`dict
        <https://docs.python.org/3/library/stdtypes.html#dict>`_* or
        **list of dict*) – One or more dictionaries containing the
        keyword arguments for the atomman.defect.point() function to
        generate specific point defect configuration(s).

      * **cutoff** (`float
        <https://docs.python.org/3/library/functions.html#float>`_) –
        Cutoff distance to use in identifying neighbor atoms.

      * **tol** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – Absolute tolerance to use for identifying if a
        defect has reconfigured (default is 1e-5 Angstoms).

   :Returns:
      Dictionary of results consisting of keys:

      * **’has_reconfigured’** (*bool*) - Flag indicating if the
        structure has been identified as relaxing to a different
        defect configuration.

      * **’centrosummation’** (*numpy.array of float*) - The
        centrosummation parameter used for evaluating if the
        configuration has relaxed.

      * **’position_shift’** (*numpy.array of float*) - The
        position_shift parameter used for evaluating if the
        configuration has relaxed. Only given for interstitial and
        substitutional-style defects.

      * **’db_vect_shift’** (*numpy.array of float*) - The
        db_vect_shift parameter used for evaluating if the
        configuration has relaxed. Only given for dumbbell-style
        defects.

   :Return type:
      `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_

**main(*args)**

   Main function called when script is executed directly.

**pointdefect(lammps_command, system, potential, point_kwargs,
mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
dmax=0.01)**

   Adds one or more point defects to a system and evaluates the defect
   formation energy.

   :Parameters:
      * **lammps_command** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_) –
        Command for running LAMMPS.

      * **system** (*atomman.System*) – The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) – The LAMMPS
        implemented potential to use.

      * **point_kwargs** (`dict
        <https://docs.python.org/3/library/stdtypes.html#dict>`_* or
        **list of dict*) – One or more dictionaries containing the
        keyword arguments for the atomman.defect.point() function to
        generate specific point defect configuration(s).

      * **mpi_command** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The MPI command for running LAMMPS in parallel.
        If not given, LAMMPS will run serially.

      * **sim_directory** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The path to the directory to perform the
        simuation in.  If not given, will use the current working
        directory.

      * **etol** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The energy tolerance for the structure
        minimization. This value is unitless. (Default is 0.0).

      * **ftol** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The force tolerance for the structure
        minimization. This value is in units of force. (Default is
        0.0).

      * **maxiter** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – The maximum number of minimization iterations
        to use (default is 10000).

      * **maxeval** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – The maximum number of minimization evaluations
        to use (default is 100000).

      * **dmax** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The maximum distance in length units that any
        atom is allowed to relax in any direction during a single
        minimization iteration (default is 0.01 Angstroms).

   :Returns:
      Dictionary of results consisting of keys:

      * **’E_coh’** (*float*) - The cohesive energy of the bulk
        system.

      * **’E_ptd_f’** (*float*) - The point.defect formation energy.

      * **’E_total_base’** (*float*) - The total potential energy of
        the relaxed bulk system.

      * **’E_total_ptd’** (*float*) - The total potential energy of
        the relaxed defect system.

      * **’system_base’** (*atomman.System*) - The relaxed bulk
        system.

      * **’system_ptd’** (*atomman.System*) - The relaxed defect
        system.

      * **’dumpfile_base’** (*str*) - The filename of the LAMMPS dump
        file for the relaxed bulk system.

      * **’dumpfile_ptd’** (*str*) - The filename of the LAMMPS dump
        file for the relaxed defect system.

   :Return type:
      `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_

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

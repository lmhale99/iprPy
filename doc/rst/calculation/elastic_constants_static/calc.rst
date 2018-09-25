
calc_elastic_constants_static.py
********************************


Calculation script functions
============================

**elastic_constants_static(lammps_command, system, potential,
mpi_command=None, strainrange=1e-06, etol=0.0, ftol=0.0,
maxiter=10000, maxeval=100000, dmax=0.01)**

   Repeatedly runs the ELASTIC example distributed with LAMMPS until
   box dimensions converge within a tolerance.

   :Parameters:
      * **lammps_command** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_) –
        Command for running LAMMPS.

      * **system** (*atomman.System*) – The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) – The LAMMPS
        implemented potential to use.

      * **mpi_command** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The MPI command for running LAMMPS in parallel.
        If not given, LAMMPS will run serially.

      * **strainrange** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The small strain value to apply when
        calculating the elastic constants (default is 1e-6).

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

      * **’a_lat’** (*float*) - The relaxed a lattice constant.

      * **’b_lat’** (*float*) - The relaxed b lattice constant.

      * **’c_lat’** (*float*) - The relaxed c lattice constant.

      * **’alpha_lat’** (*float*) - The alpha lattice angle.

      * **’beta_lat’** (*float*) - The beta lattice angle.

      * **’gamma_lat’** (*float*) - The gamma lattice angle.

      * **’E_coh’** (*float*) - The cohesive energy of the relaxed
        system.

      * **’stress’** (*numpy.array*) - The measured stress state of
        the relaxed system.

      * **’C_elastic’** (*atomman.ElasticConstants*) - The relaxed
        system’s elastic constants.

      * **’system_relaxed’** (*atomman.System*) - The relaxed system.

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


calc_relax_static.py
********************


Calculation script functions
============================

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

**relax_static(lammps_command, system, potential, mpi_command=None,
p_xx=0.0, p_yy=0.0, p_zz=0.0, p_xy=0.0, p_xz=0.0, p_yz=0.0,
dispmult=0.0, etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
dmax=0.01, maxcycles=100, ctol=1e-10)**

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

      * **p_xx** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the x tensile pressure
        component to (default is 0.0).

      * **p_yy** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the y tensile pressure
        component to (default is 0.0).

      * **p_zz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the z tensile pressure
        component to (default is 0.0).

      * **p_xy** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the xy shear pressure
        component to (default is 0.0).

      * **p_xz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the xz shear pressure
        component to (default is 0.0).

      * **p_yz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the yz shear pressure
        component to (default is 0.0).

      * **dispmult** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – Multiplier for applying a random displacement
        to all atomic positions prior to relaxing. Default value is
        0.0.

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

      * **pressure_unit** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The unit of pressure to calculate the elastic
        constants in (default is ‘GPa’).

      * **maxcycles** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – The maximum number of times the minimization
        algorithm is called. Default value is 100.

      * **ctol** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The relative tolerance used to determine if the
        lattice constants have converged (default is 1e-10).

   :Returns:
      Dictionary of results consisting of keys:

      * **’relaxed_system’** (*float*) - The relaxed system.

      * **’E_coh’** (*float*) - The cohesive energy of the relaxed
        system.

      * **’measured_pxx’** (*float*) - The measured x tensile pressure
        of the relaxed system.

      * **’measured_pyy’** (*float*) - The measured y tensile pressure
        of the relaxed system.

      * **’measured_pzz’** (*float*) - The measured z tensile pressure
        of the relaxed system.

      * **’measured_pxy’** (*float*) - The measured xy shear pressure
        of the relaxed system.

      * **’measured_pxz’** (*float*) - The measured xz shear pressure
        of the relaxed system.

      * **’measured_pyz’** (*float*) - The measured yz shear pressure
        of the relaxed system.

   :Return type:
      `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_

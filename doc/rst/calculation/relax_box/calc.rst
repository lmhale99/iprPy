
calc_relax_box.py
*****************


Calculation script functions
============================

**calc_cij(lammps_command, system, potential, mpi_command=None,
p_xx=0.0, p_yy=0.0, p_zz=0.0, strainrange=1e-06, cycle=0)**

   Runs cij.in LAMMPS script to evaluate Cij, and E_coh of the current
   system, and define a new system with updated box dimensions to
   test.

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

      * **cycle** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – Indicates the iteration cycle of quick_a_Cij().
        This is used to uniquely save the LAMMPS input and output
        files.

   :Returns:
      Dictionary of results consisting of keys:

      * **’E_coh’** (*float*) - The cohesive energy of the supplied
        system.

      * **’stress’** (*numpy.array*) - The measured stress state of
        the supplied system.

      * **’C_elastic’** (*atomman.ElasticConstants*) - The supplied
        system’s elastic constants.

      * **’system_new’** (*atomman.System*) - System with updated box
        dimensions.

   :Return type:
      `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_

   :Raises:
      `RuntimeError
      <https://docs.python.org/3/library/exceptions.html#RuntimeError>`_
      – If any of the new box dimensions are less than zero.

**main(*args)**

   Main function  called when script is executed directly.

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

**relax_box(lammps_command, system, potential, mpi_command=None,
strainrange=1e-06, p_xx=0.0, p_yy=0.0, p_zz=0.0, p_xy=0.0, p_xz=0.0,
p_yz=0.0, tol=1e-10, diverge_scale=3.0)**

   Quickly refines static orthorhombic system by evaluating the
   elastic constants and the virial pressure.

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

      * **tol** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The relative tolerance used to determine if the
        lattice constants have converged (default is 1e-10).

      * **diverge_scale** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – Factor to identify if the system’s dimensions
        have diverged.  Divergence is identified if either any current
        box dimension is greater than the original dimension
        multiplied by diverge_scale, or if any current box dimension
        is less than the original dimension divided by diverge_scale.
        (Default is 3.0).

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

   :Raises:
      `RuntimeError
      <https://docs.python.org/3/library/exceptions.html#RuntimeError>`_
      – If system diverges or no convergence reached after 100 cycles.

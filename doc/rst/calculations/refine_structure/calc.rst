
calc_refine_structure.py
************************


Calculation script functions
============================

**calc_cij(lammps_command, system, potential, symbols,
mpi_command=None, p_xx=0.0, p_yy=0.0, p_zz=0.0, strainrange=1e-06,
cycle=0)**

   Runs cij.in LAMMPS script to evaluate Cij, and E_coh of the current
   system, and define a new system with updated box dimensions to
   test.

   :Parameters:
      * **lammps_command** (*str*) -- Command for running LAMMPS.

      * **system** (*atomman.System*) -- The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) -- The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **mpi_command** (*str**, **optional*) -- The MPI command for
        running LAMMPS in parallel.  If not given, LAMMPS will run
        serially.

      * **strainrange** (*float**, **optional*) -- The small strain
        value to apply when calculating the elastic constants (default
        is 1e-6).

      * **p_xx** (*float**, **optional*) -- The value to relax the x
        tensile pressure component to (default is 0.0).

      * **p_yy** (*float**, **optional*) -- The value to relax the y
        tensile pressure component to (default is 0.0).

      * **p_zz** (*float**, **optional*) -- The value to relax the z
        tensile pressure component to (default is 0.0).

      * **cycle** (*int**, **optional*) -- Indicates the iteration
        cycle of quick_a_Cij().  This is used to uniquely save the
        LAMMPS input and output files.

   :Returns:
      Dictionary of results consisting of keys:

      * **'E_coh'** (*float*) - The cohesive energy of the supplied
        system.

      * **'stress'** (*numpy.array*) - The measured stress state of
        the supplied system.

      * **'C_elastic'** (*atomman.ElasticConstants*) - The supplied
        system's elastic constants.

      * **'system_new'** (*atomman.System*) - System with updated box
        dimensions.

   :Return type:
      dict

   :Raises:
      ``RuntimeError`` -- If any of the new box dimensions are less
      than zero.

**main(*args)**

   Main function called when script is executed directly.

**process_input(input_dict, UUID=None, build=True)**

   Processes str input parameters, assigns default values if needed,
   and generates new, more complex terms as used by the calculation.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing the
        calculation input parameters with string values.  The allowed
        keys depends on the calculation style.

      * **UUID** (*str**, **optional*) -- Unique identifier to use for
        the calculation instance.  If not given and a 'UUID' key is
        not in input_dict, then a random UUID4 hash tag will be
        assigned.

      * **build** (*bool**, **optional*) -- Indicates if all complex
        terms are to be built.  A value of False allows for default
        values to be assigned even if some inputs required by the
        calculation are incomplete.  (Default is True.)

**quick_a_Cij(lammps_command, system, potential, symbols,
mpi_command=None, ucell=None, strainrange=1e-06, p_xx=0.0, p_yy=0.0,
p_zz=0.0, tol=1e-10, diverge_scale=3.0)**

   Quickly refines static orthorhombic system by evaluating the
   elastic constants and the virial pressure.

   :Parameters:
      * **lammps_command** (*str*) -- Command for running LAMMPS.

      * **system** (*atomman.System*) -- The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) -- The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **mpi_command** (*str**, **optional*) -- The MPI command for
        running LAMMPS in parallel.  If not given, LAMMPS will run
        serially.

      * **ucell** (*atomman.System**, **optional*) -- The fundamental
        unit cell correspodning to system.  This is used to convert
        system dimensions to cell dimensions. If not given, ucell will
        be taken as system.

      * **strainrange** (*float**, **optional*) -- The small strain
        value to apply when calculating the elastic constants (default
        is 1e-6).

      * **p_xx** (*float**, **optional*) -- The value to relax the x
        tensile pressure component to (default is 0.0).

      * **p_yy** (*float**, **optional*) -- The value to relax the y
        tensile pressure component to (default is 0.0).

      * **p_zz** (*float**, **optional*) -- The value to relax the z
        tensile pressure component to (default is 0.0).

      * **tol** (*float**, **optional*) -- The relative tolerance used
        to determine if the lattice constants have converged (default
        is 1e-10).

      * **diverge_scale** (*float**, **optional*) -- Factor to
        identify if the system's dimensions have diverged.  Divergence
        is identified if either any current box dimension is greater
        than the original dimension multiplied by diverge_scale, or if
        any current box dimension is less than the original dimension
        divided by diverge_scale. (Default is 3.0).

   :Returns:
      Dictionary of results consisting of keys:

      * **'a_lat'** (*float*) - The relaxed a lattice constant.

      * **'b_lat'** (*float*) - The relaxed b lattice constant.

      * **'c_lat'** (*float*) - The relaxed c lattice constant.

      * **'alpha_lat'** (*float*) - The alpha lattice angle.

      * **'beta_lat'** (*float*) - The beta lattice angle.

      * **'gamma_lat'** (*float*) - The gamma lattice angle.

      * **'E_coh'** (*float*) - The cohesive energy of the relaxed
        system.

      * **'stress'** (*numpy.array*) - The measured stress state of
        the relaxed system.

      * **'C_elastic'** (*atomman.ElasticConstants*) - The relaxed
        system's elastic constants.

      * **'system_relaxed'** (*atomman.System*) - The relaxed system.

   :Return type:
      dict

   :Raises:
      ``RuntimeError`` -- If system diverges or no convergence reached
      after 100 cycles.

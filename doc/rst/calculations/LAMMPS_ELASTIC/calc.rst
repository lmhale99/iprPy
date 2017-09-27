
calc_LAMMPS_ELASTIC.py
**********************


Calculation script functions
============================

**lammps_ELASTIC(lammps_command, system, potential, symbols,
mpi_command=None, ucell=None, strainrange=1e-06, etol=0.0, ftol=0.0,
maxiter=10000, maxeval=100000, dmax=0.01, pressure_unit='GPa')**

   Sets up and runs the ELASTIC example distributed with LAMMPS.

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

      * **etol** (*float**, **optional*) -- The energy tolerance for
        the structure minimization. This value is unitless. (Default
        is 0.0).

      * **ftol** (*float**, **optional*) -- The force tolerance for
        the structure minimization. This value is in units of force.
        (Default is 0.0).

      * **maxiter** (*int**, **optional*) -- The maximum number of
        minimization iterations to use (default is 10000).

      * **maxeval** (*int**, **optional*) -- The maximum number of
        minimization evaluations to use (default is 100000).

      * **dmax** (*float**, **optional*) -- The maximum distance in
        length units that any atom is allowed to relax in any
        direction during a single minimization iteration (default is
        0.01 Angstroms).

      * **pressure_unit** (*str**, **optional*) -- The unit of
        pressure to calculate the elastic constants in (default is
        'GPa').

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

**lammps_ELASTIC_refine(lammps_command, system, potential, symbols,
mpi_command=None, ucell=None, strainrange=1e-06, etol=0.0, ftol=0.0,
maxiter=10000, maxeval=100000, dmax=0.01, pressure_unit='GPa',
tol=1e-10)**

   Repeatedly runs the ELASTIC example distributed with LAMMPS until
   box dimensions converge within a tolerance.

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

      * **etol** (*float**, **optional*) -- The energy tolerance for
        the structure minimization. This value is unitless. (Default
        is 0.0).

      * **ftol** (*float**, **optional*) -- The force tolerance for
        the structure minimization. This value is in units of force.
        (Default is 0.0).

      * **maxiter** (*int**, **optional*) -- The maximum number of
        minimization iterations to use (default is 10000).

      * **maxeval** (*int**, **optional*) -- The maximum number of
        minimization evaluations to use (default is 100000).

      * **dmax** (*float**, **optional*) -- The maximum distance in
        length units that any atom is allowed to relax in any
        direction during a single minimization iteration (default is
        0.01 Angstroms).

      * **pressure_unit** (*str**, **optional*) -- The unit of
        pressure to calculate the elastic constants in (default is
        'GPa').

      * **tol** (*float**, **optional*) -- The relative tolerance used
        to determine if the lattice constants have converged (default
        is 1e-10).

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

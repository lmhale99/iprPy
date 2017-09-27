
calc_dislocation_monopole.py
****************************


Calculation script functions
============================

**anneal_info(temperature=0.0, randomseed=None, units='metal')**

   Generates LAMMPS commands for thermo anneal.

   :Parameters:
      * **temperature** (*float**, **optional*) -- The temperature to
        relax at (default is 0.0).

      * **randomseed** (*int** or **None**, **optional*) -- Random
        number seed used by LAMMPS in creating velocities and with the
        Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)

      * **units** (*str**, **optional*) -- The LAMMPS units style to
        use (default is 'metal').

   :Returns:
      The generated LAMMPS input lines for performing a dynamic relax.
      Will be '' if temperature==0.0.

   :Return type:
      str

**disl_boundary_fix(system, symbols, bwidth, bshape='circle')**

   Creates a boundary region by changing atom types.

   :Parameters:
      * **system** (*atomman.System*) -- The system to add the
        boundary region to.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **bwidth** (*float*) -- The minimum thickness of the boundary
        region.

      * **bshape** (*str**, **optional*) -- The shape to make the
        boundary region.  Options are 'circle' and 'rect' (default is
        'circle').

**disl_relax(lammps_command, system, potential, symbols,
mpi_command=None, annealtemp=0.0, randomseed=None, etol=0.0,
ftol=1e-06, maxiter=10000, maxeval=100000, dmax=0.01)**

   Sets up and runs the disl_relax.in LAMMPS script for relaxing a
   dislocation monopole system.

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

      * **annealtemp** (*float**, **optional*) -- The temperature to
        perform a dynamic relaxation at. (Default is 0.0, which will
        skip the dynamic relaxation.)

      * **randomseed** (*int** or **None**, **optional*) -- Random
        number seed used by LAMMPS in creating velocities and with the
        Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)

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

   :Returns:
      Dictionary of results consisting of keys:

      * **'logfile'** (*str*) - The name of the LAMMPS log file.

      * **'dumpfile'** (*str*) - The name of the LAMMPS dump file for
        the relaxed system.

      * **'E_total'** (*float*) - The total potential energy for the
        relaxed system.

   :Return type:
      dict

**dislocationmonopole(lammps_command, system, potential, symbols,
burgers, C, mpi_command=None, axes=None, randomseed=None, etol=0.0,
ftol=0.0, maxiter=10000, maxeval=100000, dmax=0.01, annealtemp=0.0,
bshape='circle', bwidth=10.0)**

   Creates and relaxes a dislocation monopole system.

   :Parameters:
      * **lammps_command** (*str*) -- Command for running LAMMPS.

      * **system** (*atomman.System*) -- The bulk system to add the
        defect to.

      * **potential** (*atomman.lammps.Potential*) -- The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **burgers** (*list** or **numpy.array of float*) -- The
        burgers vector for the dislocation being added.

      * **C** (*atomman.ElasticConstants*) -- The system's elastic
        constants.

      * **mpi_command** (*str** or **None**, **optional*) -- The MPI
        command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.

      * **axes** (*numpy.array of float** or **None**, **optional*) --
        The 3x3 axes used to rotate the system by during creation.  If
        given, will be used to transform burgers and C from the
        standard crystallographic orientations to the system's
        Cartesian units.

      * **randomseed** (*int** or **None**, **optional*) -- Random
        number seed used by LAMMPS in creating velocities and with the
        Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)

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

      * **annealtemp** (*float**, **optional*) -- The temperature to
        perform a dynamic relaxation at. (Default is 0.0, which will
        skip the dynamic relaxation.)

      * **bshape** (*str**, **optional*) -- The shape to make the
        boundary region.  Options are 'circle' and 'rect' (default is
        'circle').

      * **bwidth** (*float**, **optional*) -- The minimum thickness of
        the boundary region (default is 10 Angstroms).

   :Returns:
      Dictionary of results consisting of keys:

      * **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump
        file for the relaxed base system.

      * **'symbols_base'** (*list of str*) - The list of element-model
        symbols for the Potential that correspond to the base system's
        atypes.

      * **'Stroh_preln'** (*float*) - The pre-logarithmic factor in
        the dislocation's self-energy expression.

      * **'Stroh_K_tensor'** (*numpy.array of float*) - The energy
        coefficient tensor based on the dislocation's Stroh solution.

      * **'dumpfile_disl'** (*str*) - The filename of the LAMMPS dump
        file for the relaxed dislocation monopole system.

      * **'symbols_disl'** (*list of str*) - The list of element-model
        symbols for the Potential that correspond to the dislocation
        monopole system's atypes.

      * **'E_total_disl'** (*float*) - The total potential energy of
        the dislocation monopole system.

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

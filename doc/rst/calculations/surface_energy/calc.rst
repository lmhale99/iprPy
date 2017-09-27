
calc_surface_energy.py
**********************


Calculation script functions
============================

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

**relax_system(lammps_command, system, potential, symbols,
mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
dmax=0.01)**

   Sets up and runs the min.in LAMMPS script for performing an
   energy/force minimization to relax a system.

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

      * **'initialdatafile'** (*str*) - The name of the LAMMPS data
        file used to import an inital configuration.

      * **'initialdumpfile'** (*str*) - The name of the LAMMPS dump
        file corresponding to the inital configuration.

      * **'finaldumpfile'** (*str*) - The name of the LAMMPS dump file
        corresponding to the relaxed configuration.

      * **'potentialenergy'** (*float*) - The total potential energy
        of the relaxed system.

   :Return type:
      dict

**surface_energy(lammps_command, system, potential, symbols,
mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
dmax=0.01, cutboxvector='c')**

   Evaluates surface formation energies by slicing along one periodic
   boundary of a bulk system.

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

      * **cutboxvector** (*str**, **optional*) -- Indicates which of
        the three system box vectors, 'a', 'b', or 'c', to cut with a
        non-periodic boundary (default is 'c').

   :Returns:
      Dictionary of results consisting of keys:

      * **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump
        file of the relaxed bulk system.

      * **'dumpfile_surf'** (*str*) - The filename of the LAMMPS dump
        file of the relaxed system containing the free surfaces.

      * **'E_total_base'** (*float*) - The total potential energy of
        the relaxed bulk system.

      * **'E_total_surf'** (*float*) - The total potential energy of
        the relaxed system containing the free surfaces.

      * **'A_surf'** (*float*) - The area of the free surface.

      * **'E_coh'** (*float*) - The cohesive energy of the relaxed
        bulk system.

      * **'E_surf_f'** (*float*) - The computed surface formation
        energy.

   :Return type:
      dict

   :Raises:
      ``ValueError`` -- For invalid cutboxvectors.
